# def make_edge(x, y, text, width):
#     return go.Scatter(x = x,
#                       y = y,
#                       line = dict(width = width, color = 'cornflowerblue'),
#                       hoverinfo = 'text',
#                       text = ([text]),
#                       mode = 'lines')
#    testament_last_move = None
    # testament_move_count = defaultdict(int)
    # testament_move_matrix = defaultdict(lambda: defaultdict(int))
    # testament_cls = None
            # if testament_cls == None:
            #     testament_cls = results[0].names
            # resultsCpu = results[0].cpu()
            # annotated_frame = results[0].plot()
            # for cls in resultsCpu.boxes.cls.numpy():
            #     if testament_cls[cls].startswith('testament_') and testament_cls[cls] != 'testament_crow':
            #         if testament_last_move != cls:
            #             testament_move_count[testament_cls[cls]] += 1
            #             if testament_last_move != None:
            #                 testament_move_matrix[testament_cls[testament_last_move]][testament_cls[cls]] += 1
            #             testament_last_move = cls
            # p1_health_bar = Bar(100, 75, 480, 20, [0,35,

#   if len(testament_move_matrix) > 0:
#         G = nx.DiGraph()
#         for node in testament_move_count:
#             G.add_node(node, size = testament_move_count[node])
#         for move in testament_move_matrix.keys():
#             for next_move in testament_move_matrix[move].keys():
#                 if testament_move_matrix[move][next_move]:
#                     G.add_edge(move, next_move, weight = testament_move_matrix[move][next_move])
#         edge_trace = []
#         pos = nx.spring_layout(G)
#         for edge in G.edges():
#             if G.edges()[edge]['weight'] > 0:
#                 move = edge[0]
#                 next_move = edge[1]
#                 x0, y0 = pos[move]
#                 x1, y1 = pos[next_move]
#                 text = move + '->' + next_move + ':' + str(G.edges()[edge]['weight'])
#                 trace = make_edge([x0, x1, None], [y0, y1, None], text, width = 0.2*G.edges()[edge]['weight'])
#                 edge_trace.append(trace)
#         node_trace = go.Scatter(x = [], y = [], text = [], textposition = "top center", textfont_size = 10, mode = 'markers+text', hoverinfo = 'none', marker = dict(color = [], size = [], line = None))
#         for node in G.nodes():
#             x, y = pos[node]
#             node_trace['x'] += tuple([x])
#             node_trace['y'] += tuple([y])
#             node_trace['marker']['color'] += tuple(['cornflowerblue'])
#             node_trace['marker']['size'] += tuple([max(G.nodes()[node]['size']/5, 1)])
#             node_trace['text'] += tuple(['<b>' + node + '</b>'])
#         layout = go.Layout(
#             paper_bgcolor='rgba(0,0,0,0)', # transparent background
#             plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
#             xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
#             yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines  
#         )
#         # Create figure
#         #fig = make_subplots(rows=1, cols=2)
#         fig = go.Figure(layout = layout)
#         # Add all edge traces
#         for trace in edge_trace:
#             fig.add_trace(trace)
#         # Add node trace
#         fig.add_trace(node_trace)
#         # Remove legend
#         fig.update_layout(showlegend = False)
#         # Remove tick labels
#         fig.update_xaxes(showticklabels = False)
#         fig.update_yaxes(showticklabels = False)
#         # Show figure
#         fig.show()