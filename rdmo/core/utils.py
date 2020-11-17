import csv
import importlib
import logging
import os
import re
from pathlib import Path
from tempfile import mkstemp
from urllib.parse import urlparse

import pypandoc
from django.apps import apps
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger(__name__)


def get_script_alias(request):
    return request.path[:-len(request.path_info)]


def get_referer(request, default=None):
    return request.META.get('HTTP_REFERER', default)


def get_referer_path_info(request, default=''):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:
        return default

    script_alias = get_script_alias(request)
    return urlparse(referer).path[len(script_alias):]


def get_next(request):
    next = request.POST.get('next')
    current = request.path_info

    if next in (current, None):
        return get_script_alias(request) + '/'
    else:
        return get_script_alias(request) + next


def get_uri_prefix(obj):
    # needs to stay, is part of a migration
    r = settings.DEFAULT_URI_PREFIX
    if bool(obj.uri_prefix) is True:
        r = obj.uri_prefix.rstrip('/')
    return r


def join_url(base, *args):
    url = base
    for arg in args:
        url = url.rstrip('/') + '/' + arg.lstrip('/')
    return url


def get_model_field_meta(model):
    meta = {}

    for field in model._meta.get_fields():
        meta[field.name] = {}
        if hasattr(field, 'verbose_name'):
            meta[field.name]['verbose_name'] = field.verbose_name
        if hasattr(field, 'help_text'):
            meta[field.name]['help_text'] = field.help_text

    return meta


def get_languages():
    languages = []
    for i in range(5):
        try:
            language = settings.LANGUAGES[i][0], settings.LANGUAGES[i][1], 'lang%i' % (i + 1)
            languages.append(language)
        except IndexError:
            pass
    return languages


def get_language_fields(field_name):
    return [field_name + '_' + lang_field for lang_code, lang_string, lang_field in get_languages()]


def get_language_warning(obj, field):
    for lang_code, lang_string, lang_field in get_languages():
        if not getattr(obj, '%s_%s' % (field, lang_field)):
            return True
    return False


def set_export_reference_document(format, context):
    # try to get the view uri from the context
    try:
        view = context['view']
        view_uri = getattr(view, 'uri')
    except (AttributeError, KeyError, TypeError):
        view_uri = None

    refdocs = []

    if format == 'odt':
        # append view specific custom refdoc
        try:
            refdocs.append(settings.EXPORT_REFERENCE_ODT_VIEWS[view_uri])
        except KeyError:
            pass

        # append custom refdoc
        if settings.EXPORT_REFERENCE_ODT:
            refdocs.append(settings.EXPORT_REFERENCE_ODT)

    elif format == 'docx':
        # append view specific custom refdoc
        try:
            refdocs.append(settings.EXPORT_REFERENCE_DOCX_VIEWS[view_uri])
        except KeyError:
            pass

        # append custom refdoc
        if settings.EXPORT_REFERENCE_DOCX:
            refdocs.append(settings.EXPORT_REFERENCE_DOCX)

    # append the default reference docs
    refdocs.append(
        os.path.join(apps.get_app_config('rdmo').path, 'share', 'reference' + '.' + format)
    )

    # return the first file in refdocs that actually exists
    for refdoc in refdocs:
        if os.path.isfile(refdoc):
            return refdoc


def render_to_format(request, export_format, title, template_src, context):
    if export_format not in dict(settings.EXPORT_FORMATS):
        return HttpResponseBadRequest(_('This format is not supported.'))

    # render the template to a html string
    template = get_template(template_src)
    html = template.render(context)

    # remove empty lines
    html = os.linesep.join([line for line in html.splitlines() if line.strip()])

    if export_format == 'html':
        # create the response object
        response = HttpResponse(html)

    else:
        pandoc_args = []
        content_disposition = 'attachment; filename="%s.%s"' % (title, export_format)

        if export_format == 'pdf':
            # check pandoc version (the pdf arg changed to version 2)
            if pypandoc.get_pandoc_version().split('.')[0] == '1':
                pandoc_args += ['-V', 'geometry:margin=1in', '--latex-engine=xelatex']
            else:
                pandoc_args += ['-V', 'geometry:margin=1in', '--pdf-engine=xelatex']

            # display pdf in browser
            content_disposition = 'filename="%s.%s"' % (title, export_format)

        elif export_format == 'rtf':
            # rtf needs to be standalone
            pandoc_args += ['--standalone']

        # use reference document for certain file formats
        refdoc = set_export_reference_document(export_format, context)
        if refdoc is not None and (export_format == 'docx' or export_format == 'odt'):
            if pypandoc.get_pandoc_version().startswith('1'):
                pandoc_args += ['--reference-{}={}'.format(export_format, refdoc)]
            else:
                pandoc_args += ['--reference-doc={}'.format(refdoc)]

        # add the possible resource-path
        resource_path = Path(settings.MEDIA_ROOT).joinpath(context['resource_path']).as_posix()
        pandoc_args.append('--resource-path={}'.format(resource_path))

        # create a temporary file
        (tmp_fd, tmp_filename) = mkstemp('.' + export_format)

        # convert the file using pandoc
        log.info('Export %s document using args %s.', export_format, pandoc_args)
        pypandoc.convert_text(html, export_format, format='html', outputfile=tmp_filename, extra_args=pandoc_args)

        # read the temporary file
        file_handler = os.fdopen(tmp_fd, 'rb')
        file_content = file_handler.read()
        file_handler.close()

        # delete the temporary file
        os.remove(tmp_filename)

        # create the response object
        response = HttpResponse(file_content, content_type='application/%s' % export_format)
        response['Content-Disposition'] = content_disposition.encode('utf-8')

    return response


def render_to_csv(title, rows, delimiter=','):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % title

    writer = csv.writer(response, delimiter=delimiter)
    for row in rows:
        writer.writerow(
            ['' if x is None else str(x) for x in row]
        )
    return response


def return_file_response(file_path, content_type):
    file_abspath = Path(settings.MEDIA_ROOT) / file_path
    if file_abspath.exists():
        with open(file_abspath, 'rb') as fp:
            response = HttpResponse(fp.read(), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename=' + file_abspath.name
            return response
    else:
        raise Http404


def sanitize_url(s):
    # is used in the rdmo-app
    try:
        m = re.search('[a-z0-9-_]', s)
    except TypeError:
        s = ''
    else:
        if bool(m) is False:
            s = ''
        else:
            s = re.sub('/+', '/', s)
    return s


def import_class(string):
    module_name, class_name = string.rsplit('.', 1)
    return getattr(importlib.import_module(module_name), class_name)


def copy_model(instance, **kwargs):
    # get the values from instance which are not id, ForeignKeys orde M2M relations
    data = {}
    for field in instance._meta.get_fields():
        if not (field.name == 'id' or field.is_relation):
            data[field.name] = getattr(instance, field.name)

    # update with the kwargs provided to this function
    data.update(kwargs)

    # create and save new instance
    instance_copy = instance._meta.model(**data)
    instance_copy.save()

    return instance_copy
