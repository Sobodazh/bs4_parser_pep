import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from outputs import control_output
from utils import get_response, find_tag, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    main_div = find_tag(
        soup, 'section', attrs={'id': 'what-s-new-in-python'}
    )

    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'}
    )

    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):

        version_a_tag = section.find('a')
        href = version_a_tag['href']

        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        h1 = find_tag(soup, 'h1')
        dl = soup.find('dl').text
        dl_text = dl.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in a_tags:

        link = a_tag['href']

        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)

    main_tag = soup.find('div', {'role': 'main'})
    table_tag = main_tag.find('table', {'class': 'docutils'})

    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_URL)

    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    status_sum = {}
    total_peps = 0

    results = [('Статус', 'Количество')]

    for pep in tqdm(tr_tags):

        total_peps += 1

        data = list(find_tag(pep, 'abbr').text)
        preview_status = data[1:][0] if len(data) > 1 else ''

        url = urljoin(PEP_URL, find_tag(pep, 'a', attrs={
            'class': 'pep reference internal'})['href'])
        soup = get_soup(session, url)

        table_info = find_tag(soup, 'dl',
                              attrs={'class': 'rfc2822 field-list simple'})
        status_pep_page = table_info.find(
            string='Status').parent.find_next_sibling('dd').string

        status_sum[status_pep_page] = status_sum.get(status_pep_page, 0) + 1
        if status_pep_page not in EXPECTED_STATUS.get(preview_status,
                                                      'Неверный ключ'):
            error_message = (f'Несовпадающие статусы:\n'
                             f'{url}\n'
                             f'Статус в карточке: {status_pep_page}\n'
                             f'Ожидаемые статусы: '
                             f'{EXPECTED_STATUS[preview_status]}')
            logging.warning(error_message)

    results.extend([(status, status_sum[status]) for status in status_sum])
    results.append(('Total', total_peps))
    return results


MODE_TO_FUNCTION = {
    'pep': pep,
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
