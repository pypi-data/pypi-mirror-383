# -*- coding: utf-8 -*-


def beforeDelete(ob, event):
    """
    Check that we can delete this inquiry...
    We can not delete an Inquiry if an UrbanEventInquiry is linked
    """
    # XXX too late???
    # XXX the code here above is useless as every references have already
    # XXX been removed here...  We use manage_beforeDelete...
    # if ob.getLinkedUrbanEventInquiry():
    #    raise BeforeDeleteException, "You can not..."


def afterDelete(ob, event):
    """
    After having deleted an Inquiry, we need to generate
    the title of the others so we have something coherent as
    the number of the inquiry is in the title
    """
    # be sure we are on a real Inquiry as some other types heritate from
    # Inquiry and so implements the IInquiry interface
    if not ob.portal_type == "Inquiry":
        return
    for inquiry in ob.getInquiries():
        if not inquiry.portal_type == "Inquiry":
            continue
        inquiry.setTitle(inquiry.generateInquiryTitle())
        inquiry.reindexObject(idxs=("title",))


def setGeneratedTitle(ob, event):
    """
    Set my title
    """
    # be sure we are on a real Inquiry as some other types heritate from
    # Inquiry and so implements the IInquiry interface
    if not ob.portal_type == "Inquiry":
        return
    ob.setTitle(ob.generateInquiryTitle())
    ob.reindexObject(idxs=("title",))


def setDefaultValuesEvent(inquiry, event):
    """
    set default values on inquiry fields
    """
    # be sure we are on a real Inquiry as some other types heritate from
    # Inquiry and so implements the IInquiry interface
    if not inquiry.portal_type == "Inquiry":
        return
    if inquiry.checkCreationFlag():
        _setDefaultSelectValues(inquiry)
        _setDefaultTextValues(inquiry)


def _setDefaultSelectValues(inquiry):
    select_fields = [
        field
        for field in inquiry.schema.fields()
        if field.default_method == "getDefaultValue"
    ]
    for field in select_fields:
        licence = inquiry.aq_inner.aq_parent
        default_value = inquiry.getDefaultValue(licence, field)
        field_mutator = getattr(inquiry, field.mutator)
        field_mutator(default_value)


def _setDefaultTextValues(inquiry):
    select_fields = [
        field
        for field in inquiry.schema.fields()
        if field.default_method == "getDefaultText"
    ]
    for field in select_fields:
        is_html = "html" in field.default_content_type
        licence = inquiry.aq_inner.aq_parent
        default_value = inquiry.getDefaultText(licence, field, is_html)
        field_mutator = getattr(inquiry, field.mutator)
        field_mutator(default_value)
