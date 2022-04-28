import pandas as pd
import plotly.express as px
from scipy.stats import mannwhitneyu


def get_pval_by_survey(data_df, col_name):
    """
    Runs a mann whitney u test on specific column (by survey) and returns pval
    :param data_df: dataframe from a specific survey
    :param col_name: name of column with values
    :return:
    """
    x, y = None, None
    flag = True
    for sur in data_df['Survey'].unique():
        if flag:
            x = data_df[data_df["Survey"] == sur][col_name].to_list()
            flag = False
        y = data_df[data_df["Survey"] == sur][col_name].to_list()
    _, p = mannwhitneyu(x, y)
    return p


def create_fisher_alpha_df(df):
    df['Sample Key'] = df['Study Site'] + df['Survey'] + df['Rock number '].astype(str)
    df['Tax Key'] = df['Species'] + df['Family'] + df['Genus']
    to_fisher_alpha_df = df.pivot_table(index='Sample Key', columns='Tax Key',
                                        values='Individual Count',
                                        aggfunc='sum').fillna(0)
    to_fisher_alpha_df.to_csv(r'to_fisher_alpha_df.csv')


def compare_sites(df):
    """
    create a pie plot comparing the composition differences between the two sites
    :param df: pandas df
    """
    # divide data by sites
    iui_df = df[df['Study Site'].isin(['IUI'])]
    kisoski_df = df[df['Study Site'].isin(['KISOSKI'])]

    # create pie plot for each site
    create_site_composition_plot(kisoski_df, 'Kioski')
    create_site_composition_plot(iui_df, 'IUI')


def create_site_composition_plot(site_df, site_name):
    """
    draws a pie plot of a site with the classes which composes this site
    :param site_df: pandas dataframe of specific site
    :param site_name: name of site
    """
    site_count = int(site_df['Individual Count'].sum())
    fig = px.pie(site_df, values='Individual Count', names='Class',
                 title=f'Class Composition in {site_name} Site ({site_count} total)')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_x=0.5)
    fig.write_image(f"plots/class_composition_{site_name}.png")


def compare_tides_class_barplot(tide_df):
    """
    Creates a histogram comparing the number of individuals surveyed in high tide vs low tide
    :param tide_df: pandas df with the results of the high vs low tide experiment
    """
    high_tide = int(tide_df[df['Survey'] == 'High Tide']['Individual Count'].sum())
    low_tide = int(tide_df[df['Survey'] == 'Low Tide']['Individual Count'].sum())

    fig = px.histogram(tide_df, x='Class', y='Individual Count', facet_col="Survey",
                       log_y=True,
                       title=f"High Tide Zone Organism Composition Throughout Different Tides <br><sup>High tide total: {high_tide}, Low tide total: {low_tide}</sup>")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Individual Count (logscale)")
    fig.write_image(f"plots/tide_class_comparison.png")


def compare_times_class_barplot(time_df):
    """
    Creates a histogram comparing the number of individuals surveyed in day vs night
    :param time_df: pandas df with the results of the day vs night tide experiment
    """
    night_total = int(time_df[df['Survey'] == 'Night']['Individual Count'].sum())
    day_total = int(time_df[df['Survey'] == 'Day']['Individual Count'].sum())

    fig = px.histogram(time_df, x='Class', y='Individual Count', facet_col="Survey",
                       log_y=True,
                       title=f"Mid Tide Zone Organism Composition Throughout Day vs. Night <br><sup>Night total: {night_total}, Day total: {day_total}</sup>")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Individual Count (logscale)")
    fig.write_image(f"plots/time_class_comparison.png")


def metadata_comparison(data_df, survey_name):
    """
    Runs a metadata comparison of a specific survey
    Compares between metadata variables (e.g "Rock Diameter (cm), complexity etc.)
    :param data_df: dataframe of specific survey
    :param survey_name: name of the survey
    """
    overview_data_rock_size(data_df, survey_name)
    overview_data_rock_complexity(data_df, survey_name)
    # TODO - add rock origin (can be done with relabeling of 0,1)
    # TODO - add bottom type (can be done with relabeling of 0,1)


def overview_data_individuals_per_rock(data_df, survey_name):
    """
    Creates a boxplot comparing the number of observations per rock in a specific survey
    Important note: observations with 50 individuals or more are treated as 50.
    :param data_df: survey df
    :param survey_name: Time or Tide
    """
    data_df["Count Fixed"] = data_df['Individual Count'].where(data_df['Individual Count'] <= 50, 50)
    fig = px.box(data_df, x="Survey", y="Count Fixed", color="Survey",
                 title=f"Observations per rock\n{survey_name}")
    fig.add_hline(y=50, line_width=1, line_dash="dash", line_color="black", annotation_text="50 individuals or more",
                  annotation_position="bottom right")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title=f"Number of individuals per rock")
    p = get_pval_by_survey(data_df, "Individual Count")
    fig.add_annotation(text=f'Pval = {round(p, 3)}',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=1.07,
                       y=0.9,
                       bordercolor='black',
                       borderwidth=1)
    # fig.write_image(f"plots/{survey_name}_total_individuals_comparison.png")
    fig.show()


def overview_data_individuals_size(data_df, survey_name):
    """
    Creates a boxplot comparing the individual size in a specific survey
    Important notes:
    1. Valid only for data with organisms
    2. Species of size >0.1 were defined as species of size 0.001 for the sake of plotting
    3. Only one data point was added per observation (i.e. if we found 300 individuals of the same species in a single
    rock we will only use a single data point in this plot)
    :param data_df: survey df
    :param survey_name: Time or Tide
    """
    data_df["Size fixed (cm)"] = data_df["Size of the organism (cm)"].replace(">0.1", 0.001)
    fig = px.box(data_df, x="Survey", y="Size fixed (cm)", color="Survey",
                 title=f"Individuals size comparison\n{survey_name}")
    fig.add_hline(y=0.001, line_width=1, line_dash="dash", line_color="black",
                  annotation_text="Individuals of size <0.1cm",
                  annotation_position="bottom right")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title=f"Individual Size")
    p = get_pval_by_survey(data_df, "Size fixed (cm)")
    fig.add_annotation(text=f'Pval = {round(p, 3)}',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=1.07,
                       y=0.9,
                       bordercolor='black',
                       borderwidth=1)
    # fig.write_image(f"plots/{survey_name}_individuals size comparison.png")
    fig.show()


def overview_data_rock_size(data_df, survey_name):
    """
    metadata comparison: comparing the rock size differences in a specific experiment
    :param data_df: survey df
    :param survey_name: Time or Tide
    """
    fig = px.box(data_df, x="Survey", y="Rock Diameter (cm)", color="Survey",
                 title=f"Rock size comparison\n{survey_name}")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title=f"Rock Size (cm)")
    p = get_pval_by_survey(data_df, "Rock Diameter (cm)")
    fig.add_annotation(text=f'Pval = {round(p, 3)}',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=1.07,
                       y=0.9,
                       bordercolor='black',
                       borderwidth=1)
    # fig.write_image(f"plots/{survey_name}_rock_size_comparison.png")
    fig.show()


def overview_data_rock_complexity(data_df, survey_name):
    """
    metadata comparison: comparing the rock complexity differences in a specific experiment
    :param data_df: survey df
    :param survey_name: Time or Tide
    """
    fig = px.box(data_df, x="Survey", y="Rock Complexity (1-5)", color="Survey",
                 title=f"Rock complexity comparison\n{survey_name}")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title=f"Rock Complexity (1-lowest complexity, 5-highest complexity)")
    p = get_pval_by_survey(data_df, "Rock Complexity (1-5)")
    fig.add_annotation(text=f'Pval = {round(p, 3)}',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=1.07,
                       y=0.9,
                       bordercolor='black',
                       borderwidth=1)
    # fig.write_image(f"plots/{survey_name}_rock_complexity_comparison.png")
    fig.show()


def compare_tides_observation_diff_class_barplot(tide_df):
    """
    Counts how many different entries are there for every species.
    In other words, what is the likelihood of finding a specific species under a rock in the survey
    Comparison is between low and high tides
    :param tide_df: df of low vs high tide surveys
    """
    low_tide_dict = tide_df[df['Survey'] == 'Low Tide'].groupby("Class").count().to_dict()["Individual Count"]
    low_tide_dict = {k: v for k, v in sorted(low_tide_dict.items(), key=lambda item: item[1], reverse=True)}
    high_tide_dict = tide_df[df['Survey'] == 'High Tide'].groupby("Class").count().to_dict()["Individual Count"]
    low_tide_df = pd.DataFrame(low_tide_dict.items(), columns=['Class', 'Count'])
    low_tide_df['Tide'] = 'Low'
    high_tide_df = pd.DataFrame(high_tide_dict.items(), columns=['Class', 'Count'])
    high_tide_df['Tide'] = 'High'
    tides_class_df = pd.concat([low_tide_df, high_tide_df])

    fig = px.histogram(tides_class_df, x='Class', y='Count', color='Tide', barmode='group',
                       title=f"High Tide Zone Organism Composition Distribution")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Observations Count")
    fig.show()
    # fig.write_image(f"plots/tide_class_comparison.png")


def compare_times_observation_diff_class_barplot(tide_df):
    """
    Counts how many different entries are there for every species.
    In other words, what is the likelihood of finding a specific species under a rock in the survey
    Comparison is between day and night
    :param tide_df: df of day vs night surveys
    """
    day_tide_dict = tide_df[df['Survey'] == 'Day'].groupby("Class").count().to_dict()["Individual Count"]
    day_tide_dict = {k: v for k, v in sorted(day_tide_dict.items(), key=lambda item: item[1], reverse=True)}
    night_tide_dict = tide_df[df['Survey'] == 'Night'].groupby("Class").count().to_dict()["Individual Count"]
    day_tide_df = pd.DataFrame(day_tide_dict.items(), columns=['Class', 'Count'])
    day_tide_df['Time'] = 'Day'
    night_tide_df = pd.DataFrame(night_tide_dict.items(), columns=['Class', 'Count'])
    night_tide_df['Time'] = 'Night'
    tides_class_df = pd.concat([day_tide_df, night_tide_df])

    fig = px.histogram(tides_class_df, x='Class', y='Count', color='Time', barmode='group',
                       title=f"Mid Tide Zone Organism Composition Distribution")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Observations Count")
    fig.show()
    # fig.write_image(f"plots/tide_class_comparison.png")


if __name__ == '__main__':
    df = pd.read_excel("data.xlsx")
    # clean whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # clean null
    # NOTE - this data doesn't include observatories without animals
    # NOTE - data with full information remained and stored in 'df' variable
    print("Running results section...")
    species_df = df[df.Class.notnull()]

    # fill nan values in individual count with 0
    df['Individual Count'] = df['Individual Count'].fillna(0)
    # create fisher alpha ds

    create_fisher_alpha_df(species_df)
    # create pie plots by site
    compare_sites(species_df)
    # create comparison dataframes

    tide_df = species_df[species_df['Survey'].isin(['High Tide', 'Low Tide'])]
    time_df = species_df[species_df['Survey'].isin(['Day', 'Night'])]

    tide_df_with_zeroes = df[df['Survey'].isin(['High Tide', 'Low Tide'])]
    time_df_with_zeroes = df[df['Survey'].isin(['Day', 'Night'])]

    # create barplots
    compare_tides_class_barplot(tide_df)
    compare_times_class_barplot(time_df)

    compare_tides_observation_diff_class_barplot(tide_df)
    compare_times_observation_diff_class_barplot(time_df)

    # overview survey results
    overview_data_individuals_per_rock(tide_df_with_zeroes, "Tide")
    overview_data_individuals_size(tide_df, "Tide")
    overview_data_individuals_per_rock(time_df_with_zeroes, "Time")
    overview_data_individuals_size(time_df, "Time")

    # metadata comparison
    metadata_comparison(tide_df, "Tide")
    metadata_comparison(time_df, "Time")
