import pandas as pd
import plotly.express as px
from scipy.stats import mannwhitneyu


def get_pval_by_survey(data_df, col_name):
    """
    Runs a mann whitney u test on specific column (by survey) and returns pval
    :param data_df: dataframe from a specific survey
    :param col_name:
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
    # divide data by sites
    iui_df = df[df['Study Site'].isin(['IUI'])]
    kisoski_df = df[df['Study Site'].isin(['KISOSKI'])]

    # create pie plot for each site
    create_site_composition_plot(kisoski_df, 'Kioski')
    create_site_composition_plot(iui_df, 'IUI')


def create_site_composition_plot(site_df, site_name):
    site_count = int(site_df['Individual Count'].sum())
    fig = px.pie(site_df, values='Individual Count', names='Class',
                 title=f'Class Composition in {site_name} Site ({site_count} total)')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_x=0.5)
    fig.write_image(f"plots/class_composition_{site_name}.png")


def compare_tides_class_barplot(tide_df):
    high_tide = int(tide_df[df['Survey'] == 'High Tide']['Individual Count'].sum())
    low_tide = int(tide_df[df['Survey'] == 'Low Tide']['Individual Count'].sum())

    fig = px.histogram(tide_df, x='Class', y='Individual Count', facet_col="Survey",
                       log_y=True,
                       title=f"High Tide Zone Oragnism Composition Throughout Different Tides <br><sup>High tide total: {high_tide}, Low tide total: {low_tide}</sup>")
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Individual Count (logscale)")
    fig.write_image(f"plots/tide_class_comparison.png")


def compare_times_class_barplot(time_df):
    night_total = int(time_df[df['Survey'] == 'Night']['Individual Count'].sum())
    day_total = int(time_df[df['Survey'] == 'Day']['Individual Count'].sum())

    fig = px.histogram(time_df, x='Class', y='Individual Count', facet_col="Survey",
                       log_y=True,
                       title=f"Mid Tide Zone Oragnism Composition Throughout Day vs. Night <br><sup>Night total: {night_total}, Day total: {day_total}</sup>")
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


def overview_data_total_individuals(data_df, survey_name):
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
    Important notes:
    1. Valid only for data with organisms
    2. Species of size >0.1 were defined as species of size 0.001 for the sake of plotting
    3. Only one data point was added per observation (i.e. if we found 300 individuals of the same species in a single
    rock we will only use a single data point in this plot)
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


if __name__ == '__main__':
    df = pd.read_excel("data.xlsx")
    # clean whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # clean null
    # NOTE - this data doesn't include observatories without animals
    # NOTE - data with full information remained and stored in 'df' variable
    print("Running results section...")
    species_df = df[df.Class.notnull()]
    # create fisher alpha ds

    # TODO - uncomment lines
    # create_fisher_alpha_df(species_df)
    # # create pie plots by site
    # compare_sites(species_df)
    # # create comparison dataframes

    tide_df = species_df[species_df['Survey'].isin(['High Tide', 'Low Tide'])]
    time_df = species_df[species_df['Survey'].isin(['Day', 'Night'])]

    # # create barplots
    # compare_tides_class_barplot(tide_df)
    # compare_times_class_barplot(time_df)

    # overview survey results
    overview_data_total_individuals(tide_df, "Tide")
    overview_data_individuals_size(tide_df, "Tide")
    overview_data_total_individuals(time_df, "Time")
    overview_data_individuals_size(time_df, "Time")

    # metadata comparison
    metadata_comparison(tide_df, "Tide")
    metadata_comparison(time_df, "Time")
