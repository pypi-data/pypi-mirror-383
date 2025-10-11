# Copyright (c) 2025 Chen Liu
# All rights reserved.
import pandas as pd
import os
import pickle
import random
import time

from scholarly import scholarly, ProxyGenerator
from tqdm import tqdm
from multiprocessing import Pool
from typing import Any, Dict


def find_all_coauthors(scholar_id: str, num_processes: int = 1) -> Dict[str, int]:
    '''
    Step 1. Find all publications of the given Google Scholar ID.
    Step 2. Extract all unique coauthors in "Lastname, Firstname" format, and the year of their latest coauthored paper.
    Returns a dictionary: {coauthor_name: latest_year}
    '''
    # Find Google Scholar Profile using Scholar ID.
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=['publications'])
    publications = author['publications']
    author_name = author['name']
    print('Author profile found: %s, with %d publications.\n' % (author_name, len(publications)))

    # Fetch metadata for all publications.
    if num_processes > 1 and isinstance(num_processes, int):
        with Pool(processes=num_processes) as pool:
            all_publications = list(tqdm(pool.imap(__fill_publication_metadata, publications),
                                         desc='Filling metadata for your %d publications' % len(publications),
                                         total=len(publications)))
    else:
        all_publications = []
        for pub in tqdm(publications,
                        desc='Filling metadata for your %d publications' % len(publications),
                        total=len(publications)):
            all_publications.append(__fill_publication_metadata(pub))

    # Extract all coauthors from all publications with their latest publication year.
    coauthor_years = {}  # Dictionary to track latest year for each coauthor

    for pub in tqdm(all_publications, desc='Extracting coauthors from publications', total=len(all_publications)):
        if 'bib' in pub and 'author' in pub['bib']:
            authors = pub['bib']['author']

            # Get publication year
            pub_year = pub['bib'].get('pub_year', None)
            if pub_year:
                try:
                    pub_year = int(pub_year)
                except (ValueError, TypeError):
                    pub_year = None

            # Split authors by 'and' to get individual names.
            author_list = [author.strip() for author in authors.split(' and ')]

            # Add all coauthors except the primary author.
            for coauthor in author_list:
                # Remove asterisks or other special characters.
                coauthor_clean = coauthor.replace('*', '').strip()

                if coauthor_clean and coauthor_clean != author_name:
                    # Convert to "Lastname, Firstname" format.
                    formatted_name = __format_name(coauthor_clean)

                    # Update the latest year for this coauthor
                    if pub_year is not None:
                        if formatted_name not in coauthor_years:
                            coauthor_years[formatted_name] = pub_year
                        else:
                            # Keep the most recent year
                            coauthor_years[formatted_name] = max(coauthor_years[formatted_name], pub_year)
                    else:
                        # If no year available, still add the coauthor but with None
                        if formatted_name not in coauthor_years:
                            coauthor_years[formatted_name] = None

    print('\nFound %d unique coauthors.\n' % len(coauthor_years))
    return coauthor_years


def __fill_publication_metadata(pub):
    time.sleep(random.uniform(1, 5))  # Random delay to reduce risk of being blocked.
    return scholarly.fill(pub)


def __format_name(name: str) -> str:
    '''
    Convert name to "Lastname, Firstname" format.
    Handles various name formats.
    '''
    # Remove extra whitespace.
    name = ' '.join(name.split())

    # If already in "Lastname, Firstname" format, return as is.
    if ',' in name:
        return name

    # Split name into parts.
    parts = name.split()

    if len(parts) == 0:
        return name
    elif len(parts) == 1:
        # Single name (just return as is).
        return name
    else:
        # Assume last part is lastname, everything else is firstname.
        lastname = parts[-1]
        firstname = ' '.join(parts[:-1])
        return f'{lastname}, {firstname}'


def export_coauthors_to_csv(coauthor_years: Dict[str, int], csv_output_path: str) -> None:
    '''
    Step 3. Export coauthor names and their latest publication years to CSV file.
    '''
    # Create DataFrame with coauthor names and years
    data = [{'coauthor name': name, 'year of latest coauthored paper': year}
            for name, year in sorted(coauthor_years.items())]

    coauthor_df = pd.DataFrame(data)
    coauthor_df.to_csv(csv_output_path, index=False)
    print('Coauthor information exported to %s.\n' % csv_output_path)
    return


def save_cache(data: Any, fpath: str) -> None:
    '''
    Save data to cache file using pickle.
    '''
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "wb") as fd:
        pickle.dump(data, fd)


def load_cache(fpath: str) -> Any:
    '''
    Load data from cache file using pickle.
    '''
    with open(fpath, "rb") as fd:
        return pickle.load(fd)


def generate_coauthor_list(scholar_id: str,
                           csv_output_path: str = None,
                           cache_folder: str = 'cache',
                           num_processes: int = 16,
                           use_proxy: bool = False):
    '''
    Generate a CSV file containing all unique coauthors of a given Google Scholar ID
    along with the year of their latest coauthored paper.

    Parameters
    ----
    scholar_id: str
        Your Google Scholar ID.
    csv_output_path: str
        (default is 'coauthors_{scholar_id}.csv')
        The path to the output CSV file.
    cache_folder: str
        (default is 'cache')
        The folder to save intermediate results.
        Set to None if you do not want caching.
    num_processes: int
        (default is 16)
        Number of processes for parallel processing.
    use_proxy: bool
        (default is False)
        If True, we will use a scholarly proxy.
        It is necessary for some environments to avoid blocks, but it usually makes things slower.
    '''
    if csv_output_path is None:
        csv_output_path = f'coauthors_{scholar_id}.csv'

    if use_proxy:
        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg)
        print('Using proxy.\n')

    # Set up cache path.
    if cache_folder is not None:
        cache_path = os.path.join(cache_folder, scholar_id, 'coauthor_years.pkl')
    else:
        cache_path = None

    # NOTE: Step 1 & 2. Find all publications and extract unique coauthors with years.
    if cache_path is None or not os.path.exists(cache_path):
        print('No cache found for this author. Finding coauthors from scratch.\n')
        coauthor_years = find_all_coauthors(scholar_id=scholar_id, num_processes=num_processes)

        if cache_path is not None and len(coauthor_years) > 0:
            save_cache(coauthor_years, cache_path)
            print('Saved to cache: %s.\n' % cache_path)
    else:
        print('Cache found. Loading coauthor information from cache.\n')
        coauthor_years = load_cache(cache_path)
        print('Loaded from cache: %s.\n' % cache_path)
        print('Found %d unique coauthors.\n' % len(coauthor_years))

    # NOTE: Step 3. Export to CSV.
    export_coauthors_to_csv(coauthor_years, csv_output_path)
    return


if __name__ == '__main__':
    # Replace this with your Google Scholar ID.
    scholar_id = '3rDjnykAAAAJ'
    generate_coauthor_list(scholar_id,
                           cache_folder='cache',
                           num_processes=16,
                           use_proxy=False)