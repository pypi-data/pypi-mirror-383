# -*- coding: utf-8 -*-

from Products.urban import URBAN_TYPES
from Products.urban.setuphandlers import createFolderDefaultValues
from datetime import datetime
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from imio.helpers.catalog import reindexIndexes

import logging

logger = logging.getLogger("urban: migrations")

end_validity_date = datetime(2024, 3, 31)
start_validity_date = datetime(2024, 4, 1)


def migrate_vocabulary_validity_date(context):
    logger.info("starting : Update vocabulary term validity end date")
    portal_urban = api.portal.get()["portal_urban"]
    brains = api.content.find(
        portal_type="UrbanVocabularyTerm",
        review_state="disabled",
        context=portal_urban,
    )
    for brain in brains:
        term = brain.getObject()
        if term.getEndValidity() is None:
            term.setEndValidity(datetime.now())
            notify(ObjectModifiedEvent(term))
    logger.info("upgrade done!")


def migrate_vocabulary_contents(context):
    logger.info("starting : Update vocabulary contents")
    portal_urban = api.portal.get()["portal_urban"]

    # 1
    # TODO: ZACC

    # 2
    codt_article127_delays_folder = portal_urban.codt_article127.folderdelays
    for existing_delay in codt_article127_delays_folder.objectValues():
        if existing_delay.getDeadLineDelay() == 130:
            existing_delay.setEndValidity(end_validity_date)
            notify(ObjectModifiedEvent(existing_delay))
        if existing_delay.getDeadLineDelay() == 90:
            existing_delay.setEndValidity(end_validity_date)
            notify(ObjectModifiedEvent(existing_delay))

    if "115j" not in codt_article127_delays_folder.objectIds():
        codt_article127_delays_folder.invokeFactory(
            "UrbanDelay",
            id="115j",
            title=u"115 jours",
            deadLineDelay=115,
            alertDelay=20,
            startValidity=start_validity_date,
        )

    if "75j" not in codt_article127_delays_folder.objectIds():
        codt_article127_delays_folder.invokeFactory(
            "UrbanDelay",
            id="75j",
            title=u"75 jours",
            deadLineDelay=75,
            alertDelay=20,
            startValidity=start_validity_date,
        )

    # 3
    for licence_type in (
        "codt_buildlicence",
        "codt_parceloutlicence",
        "codt_urbancertificatetwo",
    ):
        licence_delays_folder = portal_urban[licence_type].folderdelays
        for existing_delay in licence_delays_folder.objectValues():
            if existing_delay.getDeadLineDelay() == 60:
                existing_delay.setEndValidity(end_validity_date)
            if existing_delay.getDeadLineDelay() == 105:
                existing_delay.setEndValidity(end_validity_date)
            if existing_delay.getDeadLineDelay() == 145:
                existing_delay.setEndValidity(end_validity_date)

        if "50j" not in licence_delays_folder.objectIds():
            licence_delays_folder.invokeFactory(
                "UrbanDelay",
                id="50j",
                title=u"50 jours",
                deadLineDelay=50,
                alertDelay=20,
                startValidity=start_validity_date,
            )
        if "95j" not in licence_delays_folder.objectIds():
            licence_delays_folder.invokeFactory(
                "UrbanDelay",
                id="95j",
                title=u"95 jours",
                deadLineDelay=95,
                alertDelay=20,
                startValidity=start_validity_date,
            )
        if "135j" not in licence_delays_folder.objectIds():
            licence_delays_folder.invokeFactory(
                "UrbanDelay",
                id="135j",
                title=u"135 jours",
                deadLineDelay=135,
                alertDelay=20,
                startValidity=start_validity_date,
            )

    # 4
    objects_list = [
        {
            "id": "EXT_COMMERCE",
            "title": u"Extension d'un commerce de détail ou d'un ensemble commercial",
            "extraValue": "EXT_COMMERCE",
            "startValidity": start_validity_date,
        }
    ]
    for licence_type in ("codt_buildlicence", "codt_urbancertificatetwo"):
        licence_townshipfoldercategories_folder = portal_urban[
            licence_type
        ].townshipfoldercategories
        createFolderDefaultValues(
            licence_townshipfoldercategories_folder,
            objects_list,
            portal_type="UrbanVocabularyTerm",
        )

    # 5
    objects_list = [
        {
            "id": "div_40_alinea_2_dash_1",
            "title": u"D.IV.40 Alinéa 2/1",
            "extraValue": u"D.IV.40 Alinéa 2/1",
            "description": u"""<p>Les demandes visant à implanter un commerce au sens de l'article D.IV.4, alinéa 1er, 8°, sont soumises à enquête publique, sauf lorsque la demande porte sur l'implantation d'un commerce de quatre-cents mètres carrés et moins soumis à permis en exécution de l'article D.IV.4, alinéa 4. </p>""",
            "startValidity": start_validity_date,
        }
    ]
    for licence_type in (
        "codt_buildlicence",
        "codt_parceloutlicence",
        "codt_urbancertificatetwo",
    ):
        licence_investigationarticles_folder = portal_urban[
            licence_type
        ].investigationarticles
        createFolderDefaultValues(
            licence_investigationarticles_folder,
            objects_list,
            portal_type="UrbanVocabularyTerm",
        )

    # 6
    existing_objects_list = [
        {
            "id": "annexe4",
            "title": u"D.IV.15. alinéa 1, 1° commune décentralisée",
        },
        {
            "id": "annexe5",
            "title": u"D.IV.15. alinéa 1, 2° SOL",
        },
        {
            "id": "annexe6",
            "title": u"D.IV.15. alinéa 1, 3° permis d'urbanisation non périmé",
        },
        {
            "id": "annexe7",
            "title": u"D.IV.15. alinéa 2, 1° zone d'enjeu communal",
        },
        {
            "id": "annexe8",
            "title": u"D.IV.15. alinéa 2, 2° enseigne, logement, abattage, travaux d'impact limité",
        },
        {
            "id": "annexe9",
            "title": u"Annexe 9 - Permis d'urbanisme dispensé d'un architecte ou autre que les demandes visées aux annexes 5 à 8",
        },
    ]
    new_objects_list = [
        # new reform terms
        {
            "id": "div_16_1a",
            "title": u"DIV.16 1° a) SD pluricommunal ou SDC qui vise l’optimisation spatiale (uniquement les actes et travaux entièrement dans une centralité)",
            "startValidity": start_validity_date,
        },
        {
            "id": "div_16_1b",
            "title": u"DIV.16 1° b) une commission communale, un GCU et soit : (1) SD pluricommunal, (2) SDC, (3) SD pluricommunal et un SDC qui a partiellement cessé de produire ses effets",
            "startValidity": start_validity_date,
        },
        {
            "id": "div_16_1c",
            "title": u"DIV.16 1° c) SOL",
            "startValidity": start_validity_date,
        },
        {
            "id": "div_16_1d",
            "title": u"DIV.16 1° d) permis d’urbanisation non périmé",
            "startValidity": start_validity_date,
        },
        {
            "id": "div_16_2",
            "title": u"DIV.16 2° pas d’écart par rapport aux schémas, à la carte d’affectation des sols, aux guides d’urbanisme ou au permis d’urbanisation, si entièrement dans une zone d’enjeu communal",
            "startValidity": start_validity_date,
        },
        {
            "id": "div_16_3",
            "title": u"DIV 16 3° pas d’écart par rapport à la carte d’affectation des sols ou au GRU",
            "startValidity": start_validity_date,
        },
    ]

    licence_exemptfdarticle_folder = portal_urban.codt_buildlicence.exemptfdarticle

    # rename old terms
    for term in existing_objects_list:
        if term["id"] in licence_exemptfdarticle_folder:
            term_obj = getattr(licence_exemptfdarticle_folder, term["id"])
            term_obj.setTitle(term["title"])
            term_obj.setEndValidity(end_validity_date)
            notify(ObjectModifiedEvent(term_obj))
    # create new terms
    createFolderDefaultValues(
        licence_exemptfdarticle_folder,
        new_objects_list,
        portal_type="UrbanVocabularyTerm",
    )

    logger.info("upgrade done!")


def remove_broken_liege_browserlayer(context):
    logger.info("starting : remove broken Liege browser layer")

    from plone.browserlayer.interfaces import ILocalBrowserLayerType
    from plone.browserlayer.utils import unregister_layer
    from zope.component import getSiteManager
    from zope.component import queryUtility

    portal = api.portal.get()
    sm = getSiteManager(portal)
    name = "Liege.urban.dataimport"

    existing = queryUtility(ILocalBrowserLayerType, name=name)
    if existing:
        unregister_layer(name=name, site_manager=sm)

    logger.info("upgrade done!")


def sort_delay_vocabularies(context):
    logger.info("starting : Sort delays vocabularies")
    portal_urban = api.portal.get().portal_urban

    def sort_delays(element):
        if element.deadLineDelay != 0:
            return element.deadLineDelay
        return 99999

    for urban_type in URBAN_TYPES:
        type_config = portal_urban[urban_type.lower()]
        if "folderdelays" not in type_config:
            continue
        folderdelays = type_config.folderdelays
        if sorted(folderdelays.values(), key=sort_delays) != folderdelays.keys():
            folderdelays.orderObjects(key="deadLineDelay")
            if "inconnu" in folderdelays:
                folderdelays.moveObjectsToBottom(["inconnu"])

    logger.info("upgrade done!")


def add_new_index_and_new_filter(context):
    from eea.facetednavigation.interfaces import ICriteria
    
    logger.info("starting : Add new index and new filter for validity date")
    setup_tool = api.portal.get_tool('portal_setup')
    setup_tool.runImportStepFromProfile(
        "profile-Products.urban:default", "catalog"
    )
    reindexIndexes(None, ["getValidityDate"])
    
    portal = api.portal.get()
    urban_folder = portal.urban
    folders = [
        getattr(urban_folder, urban_type.lower() + "s", None)
        for urban_type in URBAN_TYPES
        if getattr(urban_folder, urban_type.lower() + "s", None) is not None
    ]
    folders.append(urban_folder)
    for folder in folders:
        criterion = ICriteria(folder)
        if criterion is None:
            continue
        data = {
            "_cid_": "validity-date",
            "title": u"Date de validité",
            "hidden": False,
            "index": u"getValidityDate",
            "calYearRange": u"c-10:c+10"
        }
        criterion.add(
            wid="daterange",
            position="top",
            section="advanced",
            **data
        )

    logger.info("upgrade done!")


def install_send_mail_with_attachement_action(context):
    logger.info("starting : Install send mail with attachement action")
    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.runImportStepFromProfile(
        "profile-Products.urban:default", "browserlayer"
    )
    setup_tool.runImportStepFromProfile("profile-Products.urban:default", "actions")
    setup_tool.runImportStepFromProfile("profile-Products.urban:default", "jsregistry")
    setup_tool.runImportStepFromProfile(
        "profile-Products.urban:default", "contentrules"
    )
    logger.info("upgrade done!")
