
import pandas as pd
import plotly.express as px


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




if __name__ == '__main__':
    df = pd.read_excel("data.xlsx")
    # clean whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    # clean null
    df = df[df.Class.notnull()]
    # create fisher alpha ds
    create_fisher_alpha_df(df)
    # create pie plots by site
    compare_sites(df)
    # create comparison dataframes
    tide_df = df[df['Survey'].isin(['High Tide', 'Low Tide'])]
    time_df = df[df['Survey'].isin(['Day', 'Night'])]
    # create barplots
    compare_tides_class_barplot(tide_df)
    compare_times_class_barplot(time_df)



