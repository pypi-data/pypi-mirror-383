"""Managers."""

# pylint: disable = missing-class-docstring

from collections import namedtuple
from typing import Any, List, Optional, Tuple

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import ExpressionWrapper, F, FloatField, IntegerField, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from eveuniverse.managers import EveTypeManager
from eveuniverse.models import EveMoon

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from . import __title__
from .app_settings import (
    MOONMINING_REPROCESSING_YIELD,
    MOONMINING_USE_REPROCESS_PRICING,
)
from .constants import EveCategoryId
from .core import CalculatedExtraction
from .helpers import eve_entity_get_or_create_esi_safe

MAX_THREAD_WORKERS = 20
BULK_BATCH_SIZE = 500
logger = LoggerAddTag(get_extension_logger(__name__), __title__)

SurveyProcessResult = namedtuple(
    "SurveyProcessResult", ["moon_name", "success", "error_name"]
)


class EveOreTypeManger(EveTypeManager):
    def get_queryset(self):
        """Return ore types only."""
        return (
            super()
            .get_queryset()
            .select_related("eve_group")
            .filter(published=True)
            .filter(eve_group__eve_category_id=EveCategoryId.ASTEROID)
        )

    def update_current_prices(self, use_process_pricing: Optional[bool] = None):
        """Update current prices for all ores."""
        from .models import EveOreTypeExtras

        if use_process_pricing is None:
            use_process_pricing = MOONMINING_USE_REPROCESS_PRICING

        for obj in self.filter(published=True).select_related("market_price"):
            if use_process_pricing:
                price = obj.calc_refined_value_per_unit(MOONMINING_REPROCESSING_YIELD)
                pricing_method = EveOreTypeExtras.PricingMethod.REPROCESSED_MATERIALS
            else:
                try:
                    price = obj.market_price.average_price
                    pricing_method = EveOreTypeExtras.PricingMethod.EVE_CLIENT
                except ObjectDoesNotExist:
                    price = None
                    pricing_method = EveOreTypeExtras.PricingMethod.UNKNOWN
            EveOreTypeExtras.objects.update_or_create(
                ore_type=obj,
                defaults={"current_price": price, "pricing_method": pricing_method},
            )


class MiningLedgerRecordManager(models.Manager):
    def get_queryset(self):
        """Add calculated values to all object."""
        sum_price = ExpressionWrapper(
            F("quantity") * Coalesce(F("unit_price"), 0.0),
            output_field=FloatField(),
        )
        sum_volume = ExpressionWrapper(
            F("quantity") * F("ore_type__volume"), output_field=IntegerField()
        )
        return (
            super()
            .get_queryset()
            .select_related("ore_type", "ore_type__extras")
            .annotate(unit_price=F("ore_type__extras__current_price"))
            .annotate(total_price=Sum(sum_price, distinct=True))
            .annotate(total_volume=Sum(sum_volume, distinct=True))
        )


class MoonQuerySet(models.QuerySet):
    def selected_related_defaults(self) -> models.QuerySet:
        """Apply default select_related."""
        return self.select_related(
            "eve_moon",
            "eve_moon__eve_planet__eve_solar_system",
            "eve_moon__eve_planet__eve_solar_system__eve_constellation__eve_region",
            "refinery",
            "refinery__eve_type",
            "refinery__owner",
            "refinery__owner__corporation",
            "refinery__owner__corporation__alliance",
            "label",
        )


class MoonManagerBase(models.Manager):
    def update_moons_from_survey(self, scans: str, user: Optional[User] = None) -> bool:
        """Update moons from survey input.

        Args:
            scans: raw text input from user containing moon survey data
            user: (optional) user who submitted the data
        """
        surveys, error_name = self._parse_scans(scans)
        if surveys:
            process_results, success = self._process_surveys(surveys, user)
        else:
            process_results = None
            success = False

        if user:
            success = self._send_survey_process_report_to_user(
                process_results, error_name, user, success
            )
        return success

    @staticmethod
    def _parse_scans(scans: str) -> tuple:
        surveys = []
        try:
            lines = scans.split("\n")
            lines_ = []
            for line in lines:
                line = line.strip("\r").split("\t")
                lines_.append(line)
            lines = lines_

            # Find all groups of scans.
            if len(lines[0]) == 0 or lines[0][0] == "Moon":
                lines = lines[1:]

            sub_lists = MoonManagerBase._find_lines_that_start_a_scan(lines)

            # Separate out individual surveys
            for i, _obj in enumerate(sub_lists):
                # The First List
                if i == 0:
                    if i + 2 > len(sub_lists):
                        surveys.append(lines[sub_lists[i] :])
                    else:
                        surveys.append(lines[sub_lists[i] : sub_lists[i + 1]])
                else:
                    if i + 2 > len(sub_lists):
                        surveys.append(lines[sub_lists[i] :])
                    else:
                        surveys.append(lines[sub_lists[i] : sub_lists[i + 1]])

        except (TypeError, ValueError, KeyError, AttributeError, IndexError) as ex:
            logger.warning(
                "An issue occurred while trying to parse the surveys", exc_info=True
            )
            error_name = type(ex).__name__

        else:
            error_name = ""
        return surveys, error_name

    @staticmethod
    def _find_lines_that_start_a_scan(lines):
        sub_lists = []
        for line in lines:
            if line[0] == "":
                pass
            else:
                sub_lists.append(lines.index(line))
        return sub_lists

    def _process_surveys(
        self, surveys: list, user: Optional[User]
    ) -> Tuple[List[SurveyProcessResult], bool]:
        from .models import Moon

        overall_success = True
        process_results = []
        for survey in surveys:
            try:
                moon: Moon = self._get_or_create_from_survey(survey)
                moon_products = self._extract_moon_products(survey, moon)
                moon.update_products(moon_products, updated_by=user)
                logger.info("Added moon survey for %s", moon.name)

            except Exception as ex:  # pylint: disable = broad-exception-caught
                # FIXME: Reduce broad exception
                logger.warning(
                    "An issue occurred while processing the following moon survey: %s",
                    survey,
                    exc_info=True,
                )
                error_name = type(ex).__name__
                overall_success = success = False
                moon = None
            else:
                success = True
                error_name = None

            process_results.append(
                SurveyProcessResult(
                    moon_name=moon.name if moon else "",
                    success=success,
                    error_name=error_name,
                )
            )
        return process_results, overall_success

    def _extract_moon_products(self, survey, moon):
        from .models import EveOreType, MoonProduct

        moon_products = []
        survey = survey[1:]
        for product_data in survey:
            # Trim off the empty index at the front
            product_data = product_data[1:]
            ore_type = EveOreType.objects.get_or_create_esi(id=product_data[2])[0]
            moon_products.append(
                MoonProduct(moon=moon, amount=product_data[1], ore_type=ore_type)
            )

        return moon_products

    def _get_or_create_from_survey(self, survey):
        moon_id = survey[1][6]
        eve_moon = EveMoon.objects.get_or_create_esi(id=moon_id)[0]
        moon = self.get_or_create(eve_moon=eve_moon)[0]
        return moon

    @staticmethod
    def _send_survey_process_report_to_user(
        process_results: Optional[List[SurveyProcessResult]],
        error_name: str,
        user: User,
        success: bool,
    ) -> bool:
        message = "We have completed processing your moon survey input:\n\n"
        if process_results:
            for num, process_result in enumerate(process_results):
                moon_name = process_result.moon_name
                if process_result.success:
                    status = "OK"
                    error_name = ""
                else:
                    status = "FAILED"
                    success = False
                    error_name = f"- {process_result.error_name}"
                message += f"#{num + 1}: {moon_name}: {status} {error_name}\n"
        else:
            message += "\nProcessing failed"

        title_detail = "OK" if success else "FAILED"
        notify(
            user=user,
            title=_(f"Moon survey input processing results: {title_detail}"),
            message=message,
            level="success" if success else "danger",
        )
        return success


MoonManager = MoonManagerBase.from_queryset(MoonQuerySet)


class ExtractionQuerySet(models.QuerySet):
    def selected_related_defaults(self) -> models.QuerySet:
        """Apply default select related."""
        return self.select_related(
            "refinery",
            "refinery__moon",
            "refinery__moon__eve_moon",
            "refinery__owner",
            "refinery__owner__corporation",
            "refinery__owner__corporation__alliance",
            "refinery__moon__label",
        )

    def update_status(self):
        """Update status of given extractions according to current time."""
        self.exclude(
            status__in=[self.model.Status.READY, self.model.Status.CANCELED]
        ).filter(
            chunk_arrival_at__lte=now(),
            auto_fracture_at__gt=now(),
        ).update(
            status=self.model.Status.READY
        )
        self.exclude(
            status__in=[self.model.Status.COMPLETED, self.model.Status.CANCELED]
        ).filter(auto_fracture_at__lte=now()).update(status=self.model.Status.COMPLETED)

    def annotate_volume(self) -> models.QuerySet:
        """Add volume of all products"""
        return self.annotate(volume=Sum("products__volume"))


class ExtractionManagerBase(models.Manager):
    def update_from_calculated(self, calculated: CalculatedExtraction) -> bool:
        """Update an extraction object from related calculated extraction
        when there is new information.

        Return True when updated, else False.
        """
        from .models import EveOreType, ExtractionProduct

        try:
            extraction = self._find_matching_extraction(calculated)
        except self.model.DoesNotExist:
            logger.debug("%s: Could not find matching extraction", calculated)
            return False

        needs_update, status_changed = self._calc_update_need_and_status_change(
            calculated, extraction
        )

        updated = False
        if needs_update:
            extraction.save()
            updated = True

        if calculated.products and (status_changed or not extraction.products.exists()):
            # preload eve ore types before transaction starts
            EveOreType.objects.bulk_get_or_create_esi(
                ids=[product.ore_type_id for product in calculated.products]
            )
            products = [
                ExtractionProduct(
                    extraction=extraction,
                    ore_type_id=product.ore_type_id,
                    volume=product.volume,
                )
                for product in calculated.products
            ]
            with transaction.atomic():
                ExtractionProduct.objects.filter(extraction=extraction).delete()
                ExtractionProduct.objects.bulk_create(
                    products, batch_size=BULK_BATCH_SIZE
                )
            extraction.update_calculated_properties()
            updated = True
        return updated

    def _find_matching_extraction(self, calculated: CalculatedExtraction) -> Any:
        if calculated.chunk_arrival_at:
            return self.get(
                refinery_id=calculated.refinery_id,
                chunk_arrival_at=calculated.chunk_arrival_at,
            )

        if calculated.auto_fracture_at:
            return self.get(
                refinery_id=calculated.refinery_id,
                auto_fracture_at=calculated.auto_fracture_at,
            )

        logger.debug(
            "%s: Not enough data to search for matching extraction", calculated
        )
        raise self.model.DoesNotExist()

    def _calc_update_need_and_status_change(self, calculated, extraction):
        needs_update = False
        if calculated.canceled_at and not extraction.canceled_at:
            extraction.canceled_at = calculated.canceled_at
            needs_update = True

        if calculated.canceled_by and not extraction.canceled_by:
            extraction.canceled_by = eve_entity_get_or_create_esi_safe(
                calculated.canceled_by
            )
            needs_update = True

        if calculated.canceled_by and not extraction.canceled_by:
            extraction.canceled_by = eve_entity_get_or_create_esi_safe(
                calculated.canceled_by
            )
            needs_update = True

        if calculated.fractured_by and not extraction.fractured_by:
            extraction.fractured_by = eve_entity_get_or_create_esi_safe(
                calculated.fractured_by
            )
            needs_update = True

        if calculated.fractured_at and not extraction.fractured_at:
            extraction.fractured_at = calculated.fractured_at
            needs_update = True

        if self.model.Status.from_calculated(calculated) != extraction.status:
            extraction.status = self.model.Status.from_calculated(calculated)
            needs_update = True
            status_changed = True
        else:
            status_changed = False

        if calculated.started_by and not extraction.started_by:
            extraction.started_by = eve_entity_get_or_create_esi_safe(
                calculated.started_by
            )
            needs_update = True
        return needs_update, status_changed


ExtractionManager = ExtractionManagerBase.from_queryset(ExtractionQuerySet)


class RefineryManager(models.Manager):
    def ids(self) -> set:
        """Return IDs of this queryset."""
        return set(self.values_list("id", flat=True))
