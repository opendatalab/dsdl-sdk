"""
plot module handles math plotting operations
"""

from termgraph import termgraph as tg

# print("# " + "Images Distribution Over Classes")
#
# tg.print_categories(['t1'] * 10, list(range(90, 100)))
#
# tg.chart(
#     # len_categories=2,
#     colors=[92, 96],
#     labels=['train', 'test'],
#     data=[[5000, 1000], [5000, 1000]],
#     args=dict(
#         width=50,
#         suffix=" images",
#         format="{:<5.2f}",
#         stacked=False,
#         vertical=False,
#         no_labels=False,
#         verbose=True,
#         version=True,
#         title='TEST CHART ssssssss',
#         verbos=True,
#         histogram=False,
#         no_values=False,
#         different_scale=False,
#     ),
#     # normal_data=[[50, 10], [50, 10]],/
# )
cli_chart_color_map = {'black': 90, 'red': 91, 'green': 92, 'yellow': 93, 'blue': 94, 'pink': 95, 'cyan': 96,
                       'white': 97, 'grey': 99}


def plt_cmd_bar(name, labels, data, y_categories, colors, y_label):
    print("# " + name)
    color_map_list = [cli_chart_color_map[x] for x in colors]
    tg.print_categories(y_categories, color_map_list)
    suffix = " " + y_label

    tg.chart(
        colors=color_map_list,
        labels=labels,
        data=data,
        args=dict(
            width=50,
            suffix=suffix,
            format="{:<5.2f}",
            stacked=False,
            vertical=False,
            no_labels=False,
            verbose=True,
            version=True,
            verbos=True,
            histogram=False,
            no_values=False,
            different_scale=False,
        ),
    )
