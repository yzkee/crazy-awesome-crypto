import sys
import pandas as pd
from loguru import logger
from urllib.parse import urlparse


def get_input_data(csv_location, ghw) -> pd.DataFrame:
    df = pd.read_csv(csv_location)
    df.columns = map(str.lower, df.columns)
    assert "githuburl" in df.columns
    assert "category" in df.columns

    duplicated_githuburls = df[df.duplicated(subset=["githuburl"])]
    duplicated_count = len(duplicated_githuburls)
    if duplicated_count > 0:
        logger.warning(
            f"Duplicate githuburl values found in csv: {duplicated_count}\n{duplicated_githuburls}"
        )
        logger.error(f"Fix up {duplicated_count} duplicates from {csv_location} and re-run.")
        sys.exit()
    else:
        logger.info("No duplicate githuburl values found in csv :)")

    df_exploded = explode_org_repos(df, ghw)
    return df_exploded


def explode_org_repos(df, ghw):
    wildcard_row_mask = df.githuburl.str.endswith("/*")
    df_normal_repos = df.drop(df[wildcard_row_mask].index)

    df_wildcard_repos = df[wildcard_row_mask]
    wildcard_repos_list = list(df_wildcard_repos.itertuples(index=False))
    # wildcard_repos_list = wildcard_repos_list[0:3]  # Testing

    star_limit = 25  # TODO: append to spreadsheet record? or dynamically calculate?
    exploded_rows = []
    logger.info(f"Expaning wildcard repos (star_limit = {star_limit})...")
    for row in wildcard_repos_list:
        org = urlparse(row.githuburl).path.lstrip("/").rstrip("/*")
        org_repos = ghw.get_org_repos(org)
        giturls = [[row.category,
                    row.subcategory,
                    "https://github.com/" + org_repo.full_name,
                    row.featured,
                    row.links,
                    row.description]
                   for org_repo in org_repos
                   if org_repo.stargazers_count >= star_limit]
        logger.info(f"Read repos for wildcard org: {org} ({len(giturls)} of {len(org_repos)} kept)")
        exploded_rows.extend(giturls)

    df_expanded_repos = pd.DataFrame(exploded_rows, columns=df_normal_repos.columns)
    print(f"Total matching wildcard repos: {len(exploded_rows)}")

    df_concat = pd.concat([df_normal_repos, df_expanded_repos])
    print(f"Total concat wildcard and normal repos: {len(df_concat.index)}")

    return df_concat