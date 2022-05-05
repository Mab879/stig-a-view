import datetime
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from urllib.parse import urlparse

import stig_a_view.base.models as base_models

NS = {'xccdf-1.2': 'http://checklists.nist.gov/xccdf/1.2', 'xccdf-1.1': 'http://checklists.nist.gov/xccdf/1.1'}


def disa_text_to_html(text: str) -> str:
    return text.replace("\n", "<br />")


def temp_rhel8():
    files = [('rhel7', 'U_RHEL_7_V3R5_STIG.zip'), ('ubuntu2004', 'U_Ubuntu_20-04_V1R2_STIG.zip')]
    d = datetime.date.fromisoformat('2021-10-22')
    for product, url in files:
        import_stig(f'http://localhost:1313/{url}', product, d)
        # import_stig('http://localhost:1313/U_RHEL_8_V1R4_STIG.zip', 'rhel7', d)


def import_stig(url: str, short_product_name: str, release_date: datetime.date) -> bool:
    url_parts = urlparse(url).path.split('_')

    zip_file_raw = urllib.request.urlopen(url).read()
    zip_data = BytesIO()
    zip_data.write(zip_file_raw)
    virtual_zip = zipfile.ZipFile(zip_data)
    folder = f'U_{url_parts[1]}_{url_parts[2]}_{url_parts[3]}'
    stig_file = virtual_zip.open(
        f'{folder}_Manual_STIG/U_{url_parts[1]}_{url_parts[2]}_STIG_{url_parts[3]}_Manual-xccdf.xml')
    tree = ET.ElementTree(ET.fromstringlist(stig_file.readlines()))
    root = tree.getroot()
    product = base_models.Product.objects.filter(short_name=short_product_name).first()
    stig, _ = base_models.Stig.objects.update_or_create(product=product, version=url_parts[3][1],
                                                        release=url_parts[3][3],
                                                        defaults={'release_date': release_date})
    stig.save()
    for group in root.findall('xccdf-1.1:Group', NS):
        for stig_xml in group.findall('xccdf-1.1:Rule', NS):
            stig_id = stig_xml.find('xccdf-1.1:version', NS).text
            srg, _ = base_models.Srg.objects.update_or_create(srg_id=group.find('xccdf-1.1:title', NS).text)
            description = "<root>"
            description += stig_xml.find('xccdf-1.1:description', NS).text.replace('&lt;', '<').replace('&gt;', '>')\
                .replace('&', '&amp;')
            description += "</root>"
            description_root = ET.ElementTree(ET.fromstring(description)).getroot()
            description = disa_text_to_html(description_root.find('VulnDiscussion').text)
            fix = disa_text_to_html(stig_xml.find('xccdf-1.1:fixtext', NS).text)
            check = disa_text_to_html(stig_xml.find('xccdf-1.1:check/xccdf-1.1:check-content', NS).text)
            cci_from_source = stig_xml.find("xccdf-1.1:ident[@system='http://cyber.mil/cci']", NS).text
            cci, _ = base_models.Cci.objects.update_or_create(cci_id=cci_from_source)
            base_models.Control.objects.update_or_create(disa_stig_id=stig_id, stig=stig
                                                         defaults={'srg': srg,
                                                                   'description': description,
                                                                   'severity': base_models.SEVERITY[
                                                                       stig_xml.attrib['severity']],
                                                                   'title': stig_xml.find('xccdf-1.1:title', NS).text,
                                                                   'fix': fix,
                                                                   'check_content': check,
                                                                   'vulnerability_id': group.attrib['id']
                                                                                    .replace('V-', ''),
                                                                   'cci': cci,
                                                                   })
    return False
