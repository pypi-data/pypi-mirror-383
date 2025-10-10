# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from DateTime import DateTime
from datetime import datetime
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from Products.urban import utils
from Products.Five import BrowserView
from Products.urban import UrbanMessage as _
from Products.urban.browser.mapview import MapView
from Products.urban.browser.licence.licenceview import LicenceView
from Products.urban.browser.table.urbantable import DocumentsTable
from Products.urban.browser.table.urbantable import AttachmentsTable
from Products.urban.browser.table.urbantable import ClaimantsTable
from Products.urban.browser.table.urbantable import RecipientsCadastreTable
from Products.urban.interfaces import IGenericLicence
from Products.urban.send_mail_action.forms import MAIL_ACTION_KEY
from Products.urban import services
from StringIO import StringIO

from plone import api
from plone.namedfile.field import NamedFile

from z3c.form import button
from z3c.form import form, field

from zope.annotation import interfaces
from zope.interface import Interface

import csv
import collections

claimants_csv_fieldnames = [
    "numerotation",
    "personTitle",
    "name1",
    "name2",
    "society",
    "street",
    "number",
    "zipcode",
    "city",
    "country",
    "email",
    "phone",
    "gsm",
    "nationalRegister",
    "claimType",
    "hasPetition",
    "outOfTime",
    "claimDate",
    "claimsText",
    "wantDecisionCopy",
]


class UrbanEventView(BrowserView):
    """
    This manage the view of UrbanEvent
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        plone_utils = api.portal.get_tool("plone_utils")
        if self.is_planned_mailing:
            plone_utils.addPortalMessage(
                _("The mailings will be ready tomorrow!"), type="warning"
            )
        # disable portlets
        self.request.set("disable_plone.rightcolumn", 1)
        self.request.set("disable_plone.leftcolumn", 1)

    def getActivatedFields(self):
        """
        Return all the activated fields of this UrbanEvent
        """
        context = aq_inner(self.context)
        linkedUrbanEventType = context.getUrbaneventtypes()
        fields = [
            i
            for i in context.schema.fields()
            if i.schemata == "default"
            and not hasattr(i, "optional")
            and i.widget.visible
            and i.widget.visible["view"] == "visible"
        ]
        for activatedField in linkedUrbanEventType.getActivatedFields():
            if not activatedField:
                continue  # in some case, there could be an empty value in activatedFields...
            field = context.getField(activatedField)
            fields.append(field)
        return fields

    def getFieldsToShow(self):
        """
        Return fields to display about the UrbanEvent
        """
        fields = [
            f for f in self.getActivatedFields() if not hasattr(f, "pm_text_field")
        ]
        return fields

    def getDateCustomLabel(self):
        """ """
        return self.context.getUrbaneventtypes().getEventDateLabel()

    def getPmFields(self):
        """
        Return activated pm fields to build the pm summary
        """
        fields = [f for f in self.getActivatedFields() if hasattr(f, "pm_text_field")]
        return fields

    def show_pm_summary(self):
        """ """
        return bool(self.getPmFields())

    def empty_pm_summary(self):
        """ """
        fields = self.getPmFields()

        for field_ in fields:
            text = field_.get(self.context)
            if text:
                return False

        return True

    def isTextField(self, field):
        return field.type == "text"

    def mayAddUrbanEvent(self):
        """
        Return True if the current user may add an UrbanEvent
        """
        context = aq_inner(self.context)
        member = api.portal.get_tool("portal_membership").getAuthenticatedMember()
        if member.has_permission("ATContentTypes: Add File", context):
            return True
        return False

    def mayAddAttachment(self):
        """
        Return True if the current user may add an attachment (File)
        """
        context = aq_inner(self.context)
        member = api.portal.get_tool("portal_membership").getAuthenticatedMember()
        if member.has_permission("ATContentTypes: Add File", context):
            return True
        return False

    def renderGeneratedDocumentsListing(self):
        event = aq_inner(self.context)
        documents = event.getDocuments()
        if not documents:
            return ""

        documentlisting = DocumentsTable(self.context, self.request, values=documents)
        documentlisting.update()
        return documentlisting.render()

    def renderAttachmentsListing(self):
        event = aq_inner(self.context)
        attachments = event.getAttachments()
        if not attachments:
            return ""

        table = AttachmentsTable(self.context, self.request, values=attachments)
        table.update()
        return table.render()

    def getListOfTemplatesToGenerate(self):
        """
        Return a list of dicts. Each dict contains all the infos needed in the html <href> tag to create the
        corresponding link for document generation
        """
        context = aq_inner(self.context)
        template_list = []
        for template in context.getTemplates():
            if template.can_be_generated(context):
                template_list.append(
                    {
                        "name": template.id.split(".")[0],
                        "title": template.Title(),
                        "class": "",
                        "href": self._generateDocumentHref(context, template),
                    }
                )

        for generated_doc in context.objectValues():
            for template in template_list:
                if generated_doc.id.startswith(template["name"]):
                    template["class"] = "urban-document-already-created"
        return template_list

    def _generateDocumentHref(self, context, template):
        """ """
        link = "{base_url}/urban-document-generation?template_uid={uid}".format(
            base_url=context.absolute_url(), uid=template.UID()
        )
        return link

    def getUrbaneventtypes(self):
        """
        Return the accessor urbanEventTypes()
        """
        context = aq_inner(self.context)
        return context.getUrbaneventtypes()

    def get_state(self):
        return api.content.get_state(self.context)

    @property
    def is_planned_mailing(self):
        planned_mailings = (
            api.portal.get_registry_record(
                "Products.urban.interfaces.IAsyncMailing.mailings_to_do"
            )
            or {}
        )
        is_planned = self.context.UID() in planned_mailings
        return is_planned

    def is_CODT2024(self):
        licence = self.context.aq_parent
        return licence.is_CODT2024()

    def is_not_CODT2024(self):
        licence = self.context.aq_parent
        return licence.is_not_CODT2024()

    def getProrogationDelay(self):
        licence = self.context.aq_parent
        return licence.getProrogationDelay()

    def getCompletenessDelay(self):
        licence = self.context.aq_parent
        return licence.getCompletenessDelay()

    def getReferFDDelay(self):
        licence = self.context.aq_parent
        return licence.getReferFDDelay()

    def getFDAdviceDelay(self):
        licence = self.context.aq_parent
        return licence.getFDAdviceDelay()

    def mail_send(self):
        annotations = interfaces.IAnnotations(self.context)
        notif = annotations.get(MAIL_ACTION_KEY, None)
        if notif is None or len(notif) == 0:
            return False

        notif.sort(key=lambda elem: elem["time"])
        user = notif[-1].get("user")
        username = notif[-1].get("username", None)
        if username is None or username == "":
            username = user

        return _(
            "Mail already send for ${title} by ${user}, ${date}",
            mapping={
                "title": safe_unicode(notif[-1]["title"].lower()),
                "user": safe_unicode(username),
                "date": notif[-1]["time"].strftime("%d/%m/%Y, %H:%M:%S")
            }
        )


class IImportClaimantListingForm(Interface):

    listing_file_claimants = NamedFile(title=_(u'Listing file (claimants)'))


class ImportClaimantListingForm(form.Form):

    method = "post"
    fields = field.Fields(IImportClaimantListingForm)
    ignoreContext = True

    @button.buttonAndHandler(_('Import'), name='import-claimants')
    def handleImport(self, action):
        inquiry_UID = self.context.UID()
        planned_claimants_import = (
            api.portal.get_registry_record(
                "Products.urban.interfaces.IAsyncClaimantsImports.claimants_to_import"
            )
            or []
        )
        data, errors = self.extractData()
        if errors:
            interfaces.IAnnotations(self.context)["urban.claimants_to_import"] = ""
            if inquiry_UID in planned_claimants_import:
                planned_claimants_import.remove(inquiry_UID)
        else:
            csv_file = data['listing_file_claimants']
            csv_integrity_error = self.validate_csv_integrity(csv_file)
            if csv_integrity_error:
                api.portal.show_message(csv_integrity_error, self.request, "error")
            else:
                interfaces.IAnnotations(self.context)[
                    "urban.claimants_to_import"
                ] = csv_file.data
                if inquiry_UID not in planned_claimants_import:
                    planned_claimants_import.append(inquiry_UID)
        api.portal.set_registry_record(
            "Products.urban.interfaces.IAsyncClaimantsImports.claimants_to_import",
            planned_claimants_import,
        )
        return not bool(errors)

    def validate_csv_integrity(self, csv_file):
        if csv_file.contentType not in ("text/csv"):
            return _(
                u"The imported file (${name}) doesn't appear to be a CSV file.",
                mapping={u"name": csv_file.filename},
            )

        try:
            # warning: extra or missing columns don't generate an error during CSV reading
            reader = csv.DictReader(
                StringIO(csv_file.data),
                claimants_csv_fieldnames,
                delimiter=",",
                quotechar='"',
            )
            claimant_args = [
                row for row in reader if row["name1"] or row["name2"] or row["society"]
            ][1:]
        except csv.Error as error:
            return _(
                u"The imported file (${name}) couldn't be read properly. Please verify its structure and try again.",
                mapping={u"name": csv_file.filename},
            )

        return None


class IImportRecipientListingForm(Interface):

    listing_file_recipients = NamedFile(title=_(u"Listing file (recipients)"))


class ImportRecipientListingForm(form.Form):

    method = "post"
    fields = field.Fields(IImportRecipientListingForm)
    ignoreContext = True

    @button.buttonAndHandler(_("Import"), name="import-recipients")
    def handleImport(self, action):
        self.import_recipients_from_csv()
        self.request.response.redirect(
            self.context.absolute_url()
            + "/#fieldsetlegend-urbaneventinquiry_recipients"
        )

    def import_recipients_from_csv(self):
        data, errors = self.extractData()
        if errors:
            return False

        fieldnames = [
            "name",
            "firstname",
            "street",
            "number",
            "number_index",
            "zipcode",
            "city",
            "country",
            "status",
            "id",  # extra, is read as an empty column
        ]

        csv_file = data["listing_file_recipients"]
        data = csv_file.data
        if data:
            reader = csv.DictReader(
                StringIO(data), fieldnames, delimiter=",", quotechar='"'
            )
        else:
            reader = []

        try:
            recipient_args = [row for row in reader if row["name"]][1:]
        except csv.Error, error:
            IStatusMessage(self.request).addStatusMessage(
                _(
                    u"The CSV file couldn't be read properly. Please verify its structure and try again."
                ),
                type="error",
            )
            return

        portal_urban = api.portal.get_tool("portal_urban")
        plone_utils = api.portal.get_tool("plone_utils")

        country_mapping = {"": ""}
        country_folder = portal_urban.country
        for country_obj in country_folder.objectValues():
            country_mapping[country_obj.Title()] = country_obj.id

        for recipient_arg in recipient_args:

            if not recipient_arg["id"]:
                recipient_arg["id"] = plone_utils.normalizeString(
                    " ".join([recipient_arg["name"], recipient_arg["firstname"]])
                )
                if recipient_arg["id"] in self.context.objectIds():
                    count = 1
                    new_id = "{0}-{1}".format(recipient_arg["id"], count)
                    while new_id in self.context.objectIds():
                        count += 1
                        new_id = "{0}-{1}".format(recipient_arg["id"], count)
                    recipient_arg["id"] = new_id

            recipient_arg["country"] = country_mapping.get(
                recipient_arg["country"], None
            )  # ignore country if it's missing in the country vocabulary
            recipient_arg["adr1"] = "{} {}".format(
                recipient_arg["zipcode"], recipient_arg["city"]
            )
            adr2 = "{} {}".format(
                recipient_arg["street"], recipient_arg["number"]
            )
            if recipient_arg["number_index"]:
                adr2 = "{} ({})".format(adr2, recipient_arg["number_index"])
            recipient_arg["adr2"] = adr2
            # create recipient
            with api.env.adopt_roles(["Manager"]):
                recipient_id = self.context.invokeFactory(
                    "RecipientCadastre", **recipient_arg
                )
                recipient_obj = getattr(self.context, recipient_id)

        plone_utils.addPortalMessage(_("urban_imported_recipients"), type="info")


class UrbanEventInquiryBaseView(UrbanEventView, MapView, LicenceView):
    """
    This manage the base view of UrbanEventInquiry
    """

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.request.set("disable_plone.rightcolumn", 1)
        self.request.set("disable_plone.leftcolumn", 1)
        self.import_claimants_listing_form = ImportClaimantListingForm(context, request)
        self.import_claimants_listing_form.update()
        self.import_recipients_listing_form = ImportRecipientListingForm(context, request)
        self.import_recipients_listing_form.update()

    @property
    def has_planned_claimant_import(self):
        planned_claimants_import = (
            api.portal.get_registry_record(
                "Products.urban.interfaces.IAsyncClaimantsImports.claimants_to_import"
            )
            or []
        )
        is_planned = self.context.UID() in planned_claimants_import
        return is_planned

    def import_claimants_from_csv(self):
        portal_urban = api.portal.get_tool("portal_urban")
        site = api.portal.get()

        titles_mapping = {"": ""}
        titles_folder = portal_urban.persons_titles
        for title_obj in titles_folder.objectValues():
            titles_mapping[title_obj.Title()] = title_obj.id

        country_mapping = {"": ""}
        country_folder = portal_urban.country
        for country_obj in country_folder.objectValues():
            country_mapping[country_obj.Title()] = country_obj.id

        claim_type_mapping = {
            "Écrite": "writedClaim",
            "Orale": "oralClaim",
        }

        claimants_file = interfaces.IAnnotations(self.context)[
            "urban.claimants_to_import"
        ]
        if claimants_file:
            reader = csv.DictReader(
                StringIO(claimants_file),
                claimants_csv_fieldnames,
                delimiter=",",
                quotechar='"',
            )
        else:
            reader = []
        claimant_args = [
            row for row in reader if row["name1"] or row["name2"] or row["society"]
        ][1:]
        for claimant_arg in claimant_args:
            claimant_arg.pop(None, None)
            # default values
            if not claimant_arg["claimType"]:
                claimant_arg["claimType"] = "Écrite"
            claimant_arg["hasPetition"] = bool(claimant_arg["hasPetition"])
            claimant_arg["outOfTime"] = bool(claimant_arg["outOfTime"])
            claimant_arg["wantDecisionCopy"] = bool(claimant_arg["wantDecisionCopy"])
            # mappings
            claimant_arg["personTitle"] = titles_mapping[claimant_arg["personTitle"]]
            claimant_arg["country"] = country_mapping[claimant_arg["country"]]
            claimant_arg["id"] = site.plone_utils.normalizeString(
                claimant_arg["name1"] + claimant_arg["name2"] + claimant_arg["society"]
            )
            claimant_arg["claimType"] = claim_type_mapping[claimant_arg["claimType"]]
            claimant_arg["claimDate"] = self.change_date_str_from_eu_to_us(claimant_arg["claimDate"])
            count = 0
            if claimant_arg["id"] in self.context.objectIds():
                count += 1
                new_id = claimant_arg["id"] + "-" + str(count)
                while new_id in self.context.objectIds():
                    count += 1
                    new_id = claimant_arg["id"] + "-" + str(count)
                claimant_arg["id"] = new_id
            # create claimant
            with api.env.adopt_roles(["Manager"]):
                self.context.invokeFactory("Claimant", **claimant_arg)
            print "imported claimant {id}, {name} {surname}".format(
                id=claimant_arg["id"],
                name=claimant_arg["name1"],
                surname=claimant_arg["name2"],
            )

    def change_date_str_from_eu_to_us(self, date):
        try:
            return datetime.strptime(date, "%d/%m/%y").strftime("%m/%d/%y")
        except ValueError as err:
            return date

    def getParcels(self):
        context = aq_inner(self.context)
        return context.getParcels()

    def renderClaimantsListing(self):
        if not self.context.getClaimants():
            return ""
        contactlisting = ClaimantsTable(self.context, self.request)
        contactlisting.update()
        return contactlisting.render()

    def getLinkedInquiry(self):
        context = aq_inner(self.context)
        return context.getLinkedInquiry()

    def getInquiryFields(self):
        """
        This will return fields to display about the Inquiry
        """
        context = aq_inner(self.context)
        linkedInquiry = context.getLinkedInquiry()
        fields = []
        if not linkedInquiry:
            # this should not happen...
            return None
        displayed_fields = self.getUsedAttributes()
        schemata = (
            IGenericLicence.providedBy(linkedInquiry) and "urban_inquiry" or "default"
        )
        inquiry_fields = utils.getSchemataFields(
            linkedInquiry, displayed_fields, schemata
        )
        for inquiry_field in inquiry_fields:
            if inquiry_field.__name__ == "claimsText":
                # as this text can be very long, we do not want to show it with the other
                # fields, we will display it in the "Claimants" part of the template
                continue
            fields.append(inquiry_field)

        return fields

    def getInquiryReclamationNumbers(self):

        inquiryReclamationNumbers = []
        context = aq_inner(self.context)
        totalOral = 0
        totalWrite = 0
        if context.getClaimants():
            for claimant in context.getClaimants():
                if claimant.getClaimType() == "oralClaim":
                    totalOral += 1
                elif claimant.getClaimType() == "writedClaim":
                    totalWrite += 1

        inquiryReclamationNumbers.append(totalOral)
        inquiryReclamationNumbers.append(totalWrite)
        return inquiryReclamationNumbers

    def getLinkToTheInquiries(self):
        """
        This will return a link to the inquiries on the linked licence
        """
        context = aq_inner(self.context)
        return (
            context.aq_inner.aq_parent.absolute_url() + "/#fieldsetlegend-urban_inquiry"
        )

    def getLinkedInquiryTitle(self):
        """
        This will return the title of the linked Inquiry
        """
        context = aq_inner(self.context)
        linkedInquiry = context.getLinkedInquiry()
        if linkedInquiry:
            if not linkedInquiry.portal_type == "Inquiry":
                # we do not use Title as this inquiry is the licence
                return linkedInquiry.generateInquiryTitle()
            else:
                return linkedInquiry.Title()

    def check_dates_for_suspension(self):
        inquiry_event = self.context
        start_date = inquiry_event.getInvestigationStart()
        end_date = inquiry_event.getInvestigationEnd()
        if not start_date or not end_date:
            return True, "", ""

        licence = inquiry_event.aq_parent
        portal_urban = api.portal.get_tool("portal_urban")
        suspension_periods = portal_urban.getInquirySuspensionPeriods()
        suspension_delay = 0
        inquiry_duration = 15
        if hasattr(licence, "getRoadAdaptation"):
            if licence.getRoadAdaptation() and licence.getRoadAdaptation() not in [
                [""],
                "no",
            ]:
                inquiry_duration = 30
        theorical_end_date = start_date + inquiry_duration

        for suspension_period in suspension_periods:
            suspension_start = DateTime(suspension_period["from"])
            suspension_end = DateTime(suspension_period["to"])
            if start_date >= suspension_start and start_date < suspension_end + 1:
                suspension_delay = suspension_end - start_date
                if end_date < theorical_end_date + suspension_delay:
                    return False, suspension_period["from"], suspension_period["to"]
        return True, "", ""


class UrbanEventAnnouncementView(UrbanEventInquiryBaseView):
    """
    This manage the view of UrbanEventAnnouncement
    """

    def __init__(self, context, request):
        super(UrbanEventAnnouncementView, self).__init__(context, request)
        plone_utils = api.portal.get_tool("plone_utils")
        self.linkedInquiry = self.context.getLinkedInquiry()
        if not self.linkedInquiry:
            plone_utils.addPortalMessage(
                _(
                    "This UrbanEventInquiry is not linked to an existing Inquiry !  Define a new inquiry on the licence !"
                ),
                type="error",
            )
        if self.has_planned_claimant_import:
            plone_utils.addPortalMessage(
                _("The claimants import will be ready tomorrow!"), type="warning"
            )
        if self.is_planned_mailing:
            plone_utils.addPortalMessage(
                _("The mailings will be ready tomorrow!"), type="warning"
            )
        (
            suspension_check,
            suspension_start,
            suspension_end,
        ) = self.check_dates_for_suspension()
        if not suspension_check:
            plone_utils.addPortalMessage(
                _(
                    "Suspension period from to: please check the end date",
                    mapping={"from": suspension_start, "to": suspension_end},
                ),
                type="warning",
            )
        # disable portlets
        self.request.set("disable_plone.rightcolumn", 1)
        self.request.set("disable_plone.leftcolumn", 1)

    def getInquiryFields(self):
        """
        This will return fields to display about the Inquiry
        """
        context = aq_inner(self.context)
        linked_inquiry = context.getLinkedInquiry()
        fields_to_display = linked_inquiry.get_inquiry_fields_to_display()
        return fields_to_display


class UrbanEventInquiryView(UrbanEventInquiryBaseView):
    """
    This manage the view of UrbanEventInquiry
    """

    def __init__(self, context, request):
        super(UrbanEventInquiryView, self).__init__(context, request)
        plone_utils = api.portal.get_tool("plone_utils")
        self.linkedInquiry = self.context.getLinkedInquiry()
        if not self.linkedInquiry:
            plone_utils.addPortalMessage(
                _(
                    "This UrbanEventInquiry is not linked to an existing Inquiry !  Define a new inquiry on the licence !"
                ),
                type="error",
            )
        if self.hasPOWithoutAddress():
            plone_utils.addPortalMessage(
                _(
                    "There are parcel owners without any address found! Desactivate them!"
                ),
                type="warning",
            )
        if self.is_planned_inquiry:
            plone_utils.addPortalMessage(
                _("The parcel radius search will be ready tomorrow!"), type="warning"
            )
        if self.is_planned_mailing:
            plone_utils.addPortalMessage(
                _("The mailings will be ready tomorrow!"), type="warning"
            )
        if self.has_planned_claimant_import:
            plone_utils.addPortalMessage(
                _("The claimants import will be ready tomorrow!"), type="warning"
            )
        (
            suspension_check,
            suspension_start,
            suspension_end,
        ) = self.check_dates_for_suspension()
        if not suspension_check:
            plone_utils.addPortalMessage(
                _(
                    "Suspension period from to: please check the end date",
                    mapping={"from": suspension_start, "to": suspension_end},
                ),
                type="warning",
            )
        # disable portlets
        self.request.set("disable_plone.rightcolumn", 1)
        self.request.set("disable_plone.leftcolumn", 1)

    def __call__(self):
        if "find_recipients_cadastre" in self.request.form:
            radius = self.getInquiryRadius()
            return self.getInvestigationPOs(radius)
        return self.index()

    def renderRecipientsCadastreListing(self):
        recipients = self.context.getRecipients()
        if not recipients:
            return ""
        contactlisting = RecipientsCadastreTable(
            self.context, self.request, values=recipients
        )
        contactlisting.update()
        return contactlisting.render()

    def getRecipients(self):
        context = aq_inner(self.context)
        return context.getRecipients()

    def hasPOWithoutAddress(self):
        context = aq_inner(self.context)
        for parcel_owner in context.getRecipients(onlyActive=True):
            if not parcel_owner.getStreet() or not parcel_owner.getAdr1():
                return True
        return False

    @property
    def is_planned_inquiry(self):
        planned_inquiries = (
            api.portal.get_registry_record(
                "Products.urban.interfaces.IAsyncInquiryRadius.inquiries_to_do"
            )
            or {}
        )
        is_planned = self.context.UID() in planned_inquiries
        return is_planned

    def getInvestigationPOs(self, radius=0, force=False):
        """
        Search parcel owners in a radius of 50 meters...
        """
        # if we do the search again, we first delete old datas...
        # remove every RecipientCadastre
        context = aq_inner(self.context)
        urban_tool = api.portal.get_tool("portal_urban")
        recipients = context.getRecipients()
        if self.is_planned_inquiry and not force:
            return self.request.response.redirect(self.context.absolute_url())
        if recipients:
            context.manage_delObjects(
                [recipient.getId() for recipient in recipients if recipient.Title()]
            )

        licence = context.aq_inner.aq_parent
        cadastre = services.cadastre.new_session()
        neighbour_parcels = cadastre.query_parcels_in_radius(
            center_parcels=licence.getParcels(), radius=radius
        )

        if (
            not force
            and urban_tool.getAsyncInquiryRadius()
            and len(neighbour_parcels) > 40
        ):
            planned_inquiries = (
                api.portal.get_registry_record(
                    "Products.urban.interfaces.IAsyncInquiryRadius.inquiries_to_do"
                )
                or {}
            )
            planned_inquiries[self.context.UID()] = radius
            api.portal.set_registry_record(
                "Products.urban.interfaces.IAsyncInquiryRadius.inquiries_to_do",
                planned_inquiries,
            )
            return self.request.response.redirect(
                self.context.absolute_url()
                + "/#fieldsetlegend-urbaneventinquiry_recipients"
            )

        for parcel in neighbour_parcels:
            for owner_id, owner in parcel.owners.iteritems():
                name = str(owner["name"].encode("utf-8"))
                firstname = str(owner["firstname"].encode("utf-8"))
                country = str(owner["country"].encode("utf-8"))
                zipcode = str(owner["zipcode"].encode("utf-8"))
                city = str(owner["city"].encode("utf-8"))
                street = str(owner["street"].encode("utf-8"))
                number = str(owner["number"].encode("utf-8"))
                print name, firstname
                # to avoid having several times the same Recipient (that could for example be on several parcels
                # we first look in portal_catalog where Recipients are catalogued
                owner_obj = owner_id and getattr(context, owner_id, None)
                if owner_id and not owner_obj:
                    new_owner_id = context.invokeFactory(
                        "RecipientCadastre",
                        id=owner_id,
                        name=name,
                        firstname=firstname,
                        # keep adr1 and adr2 fields for historical reasons.
                        adr1="{} {}".format(zipcode, city),
                        adr2="{} {}".format(street, number),
                        number=number,
                        street=street,
                        zipcode=zipcode,
                        city=city,
                        country=country.lower(),
                        capakey=parcel.capakey,
                        parcel_street=parcel.locations
                        and parcel.locations.values()[0]["street_name"]
                        or "",
                        parcel_police_number=parcel.locations
                        and parcel.locations.values()[0]["number"]
                        or "",
                        parcel_nature=", ".join(parcel.natures),
                    )
                    owner_obj = getattr(context, new_owner_id)
                    owner_obj.setTitle("{} {}".format(name, firstname))
        cadastre.close()
        return context.REQUEST.RESPONSE.redirect(
            context.absolute_url() + "/#fieldsetlegend-urbaneventinquiry_recipients"
        )

    def getInquiryRadius(self):
        licence = self.context.aq_parent
        if hasattr(licence, "hasEnvironmentImpactStudy"):
            if licence.getHasEnvironmentImpactStudy():
                return 200
        if hasattr(licence, "impactStudy"):
            if licence.getImpactStudy():
                return 200
        if hasattr(licence, "inquiry_category"):
            if licence.getInquiry_category() == "B":
                return 200
        return 50
