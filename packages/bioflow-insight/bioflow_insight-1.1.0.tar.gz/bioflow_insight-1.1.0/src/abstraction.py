from .workflow import Workflow
from .condition import Condition
from .tree import Tree
from .cloud import Cloud
import re
from . import constant
import numpy as np
import time
import pprint


class Abstraction:
    

    def __init__(self, workflow):
        self.workflow = workflow

    def get_list_of_potential_clusters(self):
        #First start by getting all the conditions and the calls/operations and conditions associated to it
        conditions = self.workflow.get_most_influential_conditions()

        
        #Decompose the operations and call into their basic form so that for example [call1(call2(operation1))]
        #Becomes [[process1, process2, operation1]] -> of course i'm only manipulating the ids
        #The goal of this function is that from the elements in the code -> i can manipulate the elements in the graph
        def get_basic_blocks(exe, building_blocks):
            #In the case of the call -> we extract the process if one is called 
            #And decompose its parameters
            if(exe.get_type()=="Call"):
                if(exe.get_first_element_called().get_type()=="Process"):
                    building_blocks[exe.get_first_element_called()] = ""
                if(exe.get_first_element_called().get_type()=="Subworkflow"):
                    for temp in exe.get_first_element_called().get_all_executors_in_workflow():
                        get_basic_blocks(temp, building_blocks)
                for p in exe.parameters:
                    if(p.get_type() in ["Call", "Operation"]):
                        get_basic_blocks(p, building_blocks)
            #In the case of an operation -> we add it (if it's not a call to a subworkflow)
            #Plus we extract and decompose its origins
            elif(exe.get_type()=="Operation"):
                if(not(len(exe.get_origins())==1 and exe.get_origins()[0].get_type()=="Call" and exe.get_origins()[0].get_first_element_called().get_type()=="Subworkflow")):
                    if(not exe.get_artificial_status()):
                        building_blocks[exe] = ""
                for o in exe.get_origins():
                    if(o.get_type() in ["Call", "Operation"]):
                        get_basic_blocks(o, building_blocks)
            #This is for DSL1
            elif(exe.get_type()=="Process"):
                building_blocks[exe] = ""
            else:
                raise Exception("This shouldn't happen")
            return list(building_blocks.keys())
        

        for cond in conditions:
            tab = []
            names = []
            for exe in conditions[cond]:
                tab += get_basic_blocks(exe, {})
            #for t in tab:
            #    if(t.get_type()=="Operation"):
            #        names.append(t.get_code(get_OG = True))
            #    else:
            #        names.append(t.get_name())
            #print(cond.get_value(), conditions[cond][0].get_code(get_OG = True), names)
            #print(tab)
            #print()
            conditions[cond] = tab
        #print(conditions)

        
        
        
        #This function checks if there is overlapping between the conditions -> if it's the case we add the the larger overlapping group
        #It basically does an anlysis of the conditions and when there is an overlapping of the simplified conditions -> it creates a larger group:)
        def groups_conditions_together_where_possible(dico_conditions):
            conditions = list(dico_conditions)
            #print(conditions)
            #for c in conditions:
            #    print(c.get_value(), c.get_minimal_sum_of_products())
            for i in range(len(conditions)):
                for y in range(len(conditions)):
                    if(i>y):
                        cond1, cond2 = conditions[i], conditions[y]
                        #minimal_sum_of_products_1, minimal_sum_of_products_2 = cond1.get_minimal_sum_of_products(), cond2.get_minimal_sum_of_products()
                        #if(minimal_sum_of_products_1==minimal_sum_of_products_2):
                        if(cond1.get_value()==cond2.get_value()):
                            #print(cond1.get_value(), minimal_sum_of_products_1, cond1)
                            #print(cond2.get_value(), minimal_sum_of_products_2, cond2)
                            new_conditions = Condition(origin=self, condition=cond1.get_value(), artificial=True)
                            #cluster1, cluster2 = dico_conditions[cond1],  dico_conditions[cond2]
                            #new_group = cluster1+cluster2
                            dico_conditions[cond1]+=dico_conditions[cond2]
                            #dico_conditions.pop(cond1)
                            dico_conditions.pop(cond2)
                            #dico_conditions[new_conditions] = new_group
                            return True
            


            #We do an analysis of the conditions and check if there is an overlapping with the or
            dico_conditions_to_expand = {}
            for cond in conditions:
                minimal_sum_of_products = cond.get_minimal_sum_of_products()
                for mini_cond in minimal_sum_of_products:
                    try:
                        temp = dico_conditions_to_expand[str(mini_cond)] 
                    except:
                        dico_conditions_to_expand[str(mini_cond)] = []
                    dico_conditions_to_expand[str(mini_cond)].append(cond)
            #print(dico_conditions_to_expand)
            for mini_cond in dico_conditions_to_expand:
                if(len(dico_conditions_to_expand[mini_cond])>1):
                    to_remove = []
                    new_group = []
                    value = None
                    #This means we want to create a larger group
                    for cond in dico_conditions_to_expand[mini_cond]:
                        new_group += dico_conditions[cond]
                        if(len(cond.get_minimal_sum_of_products())==1):
                            value = cond.get_minimal_sum_of_products()[0]
                            to_remove.append(cond)
                            #dico_conditions.pop(cond2)
                    if(value==None):
                        for mini in dico_conditions_to_expand[mini_cond][0].get_minimal_sum_of_products():
                            if(str(mini)==mini_cond):
                                value = mini
                    new_conditions = Condition(origin=self, condition="&&".join(value), artificial=True)
                    dico_conditions[new_conditions] = list(set(new_group))
                    for r in to_remove:
                        dico_conditions.pop(r)
            

                
            #
            #for i in range(len(conditions)):
            #    for y in range(len(conditions)):
            #        if(i>y):
            #            cond1, cond2 = conditions[i], conditions[y]
            #            minimal_sum_of_products_1, minimal_sum_of_products_2 = cond1.get_minimal_sum_of_products(), cond2.get_minimal_sum_of_products()
            #            for mini_cond in minimal_sum_of_products_1:
            #                if(mini_cond in minimal_sum_of_products_2):
            #                    cluster1, cluster2 = dico_conditions[cond1],  dico_conditions[cond2]
            #                    if(len(set(cluster1).intersection(set(cluster2)))==0):
            #                        print("here")
            #                        print(minimal_sum_of_products_1, minimal_sum_of_products_2)
            #                        new_conditions = Condition(origin=self, condition="&&".join(mini_cond), artificial=True)
            #                        new_group = cluster1+cluster2
            #                        if(len(minimal_sum_of_products_1)==1 or cond1.get_artificial()):
            #                            dico_conditions.pop(cond1)
            #                        if(len(minimal_sum_of_products_2)==1 or cond2.get_artificial()):
            #                            dico_conditions.pop(cond2)
            #                        dico_conditions[new_conditions] = new_group
            #                        return True


            return False

        #pprint.pp(conditions)
        merging_conditions = True
        while(merging_conditions):
            merging_conditions = groups_conditions_together_where_possible(conditions)
        #pprint.pp(conditions)

        return conditions

    def get_condition_abtsraction(self):
        
        #STEP1 -> extract potential clusters
        conditions = self.get_list_of_potential_clusters()

        #From this point we are only manipulating elements which are in the graph
        potential_clusters = list(conditions.values())


        #STEP 1.5 -> retrieving the link dico (without artificial nodes)
        #Plus also retriving the clouds -> these are the operations which are all interconnected together to forming the clouds
        link_dico = self.workflow.graph.get_link_dico(bool_get_object = True, without_artificial_nodes = True)
        clouds = self.workflow.graph.get_clouds_wo_artificial(bool_get_object = True)

        #STEP1.6 -> replacind the clouds by a singe point of type cloud -> which will stock the operations
        #We do this cause by defintion the cloud cannot be split into different conditions
        #So to deal with this we need to simply update the link dico and the conditions dico 
        for cloud in clouds:
            cloud_node = Cloud(operations=cloud)
        
            #Adding the cloud node to the link dico
            link_dico[cloud_node] = link_dico[cloud[0]].copy() 
            #Removing all the operations from the link_dico
            for c in cloud:
                for node in link_dico:
                    if(c in link_dico[node]):
                        link_dico[node].remove(c)
                        if(cloud_node not in link_dico[node] and node!=cloud_node):
                            link_dico[node].append(cloud_node)
                link_dico.pop(c)
            
            #Updating the conditions
            to_remove = []
            for cond in conditions:
                #For a cloud to be in a condition -> the entire cloud needs to be in it
                #If only a subpart of the cloud is in a condition then we remove nodes from the condition
                if(set(cloud).issubset(set(conditions[cond]))):
                    conditions[cond].append(cloud_node)
                for node in cloud:
                    if(node in conditions[cond]):
                        conditions[cond].remove(node)
                if(conditions[cond]==[]):
                    to_remove.append(cond)
            for r in to_remove:
                conditions.pop(r)

        
                    




        #Retrieve a list of all the nodes in the workflow graph 
        all_nodes_in_graph = []
        for n in link_dico:
            all_nodes_in_graph.append(n)
            all_nodes_in_graph += link_dico[n]
        all_nodes_in_graph = list(set(all_nodes_in_graph))

        def get_largest_cluster(potential_clusters):
            if(len(potential_clusters)>0):
                largest = potential_clusters[0]
                for c in potential_clusters:
                    if(len(c)>len(largest)):
                        largest = c
                return largest
            else:
                return []
            
        
        clustering = Tree(value=None, conditions=[], children = [])
            
        #This is a function that creates a copy of a 2d list -> i don't know why the the ".copy()" doesn't work as i'm expecting it to 
        def georges_copy(list_2D):
            tab = []
            for list in list_2D:
                temp = []
                for ele in list:
                    temp.append(ele)
                tab.append(temp)
            return tab
        
        def check_all_paths_are_in_cluster(cluster, all_nodes_in_graph, link_dico):
            #Need to check that all the paths between the nodes in cluster are formed by nodes in the cluster
            for i in range(len(cluster)):
                for y in range(len(cluster)):
                    if(i!=y):
                        A, B = cluster[i], cluster[y]
                        val, paths = explore_all_paths(A, B, all_nodes_in_graph, link_dico)
                        if(val):
                            for path in paths:
                                for n in path:
                                    if(n not in cluster):
            
                                        index = path.index(n)
                                        pred = path[:index]
                                        rest = list(set(cluster)-set(pred))
                                        return False, pred, rest
            return True, [], []


        def create_cluster_rec(clustering, potential_clusters, last_cluster_created, groups_created, rec ):
            
            #Only keep the nodes in the potential_clusters which appear in the last_cluster_created
            for c in potential_clusters:
                for node in c:
                    if(node not in last_cluster_created):
                        c.remove(node)
            potential_clusters = list(filter(lambda a: a != [], potential_clusters))


            
            while(len(potential_clusters)>0):
                cluster = get_largest_cluster(potential_clusters)

                #Check that the potential cluster is larger than just one element
                if(len(cluster)>1):                    
                    all_paths_are_in_cluster, pred, rest= check_all_paths_are_in_cluster(cluster, all_nodes_in_graph, link_dico)

                    #This means the cluster can be created
                    if(all_paths_are_in_cluster):
                        tree_cluster = Tree(value=f"G{groups_created}", conditions =[], children = [])
                        groups_created+=1
                        potential_clusters.remove(cluster)
                        groups_created = create_cluster_rec(tree_cluster, georges_copy(potential_clusters), cluster.copy(), groups_created = groups_created, rec=rec+1)
                        #This doesn't work -> i don't know why fucking why
                        #groups_created = create_cluster_rec(tree_cluster, potential_clusters.copy(), cluster.copy(), groups_created = groups_created, rec=rec+1)
                        added = tree_cluster.get_all_leafs_in_tree({})
                        for a in added:
                            try:
                                cluster.remove(a)
                            except:
                                None
                        
                        tree_cluster.add_children(cluster)
                        clustering.add_child(tree_cluster)
                            
                        #Remove all the nodes which have just been added to tree 
                        values_in_tree = clustering.get_all_leafs_in_tree({})
                        for c in potential_clusters:
                            for node in c:
                                if(node in values_in_tree):
                                    c.remove(node)
                        potential_clusters = list(filter(lambda a: a != [], potential_clusters))
                    
                    else:
                        potential_clusters.append(pred)
                        potential_clusters.append(rest)
                        potential_clusters.remove(cluster)
                else:
                    potential_clusters.remove(cluster)
            return groups_created


        #Step 2 -> Create the clusters    
        groups_created = create_cluster_rec(clustering, georges_copy(potential_clusters), all_nodes_in_graph, groups_created = 1, rec = 0)
        #Adding the nodes which have been added to the groups
        leafs = clustering.get_all_leafs_in_tree(val = {})
        to_add = []
        for n in all_nodes_in_graph:
            if(n not in leafs):
                to_add.append(n)
        clustering.add_children(to_add)


        #Step 2.5 -> for each leaf in the list, add it's condition
        #The method also adds the intersection of contions to cluster (intersection of all it's nodes)
        node_2_conditions = {}
        for cond in conditions:
            for node in conditions[cond]:
                try:
                    temp = node_2_conditions[node]
                except:
                    node_2_conditions[node] = []
                node_2_conditions[node].append(cond)
        clustering.add_conditions_to_tree(node_2_conditions)



        #Step3 -> making the clusters minimal
        #We use the conditions in the tree to do this
        def merge_tree(tree, groups_created):

            children = tree.get_children()
            for i in range(len(children)):
                for y in range(len(children)):
                    if(i>y):
                        child1, child2 = children[i], children[y]
                        conditions_in_commun = child1.get_conditions_in_commun(child2)
                        for cond in conditions_in_commun:
                            if(cond not in tree.get_conditions()):
                                G1, G2 = child1.get_all_leafs_in_tree({}), child2.get_all_leafs_in_tree({})
                                all_paths_are_in_cluster, pred, rest = check_all_paths_are_in_cluster((G1+G2), all_nodes_in_graph, link_dico)
                                #This means we need to merge the 2 children together
                                if(all_paths_are_in_cluster):
                                    tree.merge_2_children_together(child1, child2, groups_created)
                                    groups_created+=1
                                    return True, groups_created
            return False, groups_created

        def make_tree_minimal(tree, groups_created, recu):           
            still_merging = True
            
            while(still_merging):
                still_merging, groups_created = merge_tree(tree, groups_created)

            for child in tree.children:
                if(not child.is_a_leaf()):
                    groups_created = make_tree_minimal(child, groups_created, recu+1)
                    None

            return groups_created

        make_tree_minimal(clustering, groups_created, recu= 0)

        #STEP3.5 -> remove the clouds and put it's operations back
        clustering.remove_clouds()

        return clustering

def get_val(node):
    if(node.get_type()=="Process"):
        return node.get_name()
    else:
        return node.get_code(get_OG = True)

def explore_all_paths_rec(A, B, links_dico, visited, paths, current_path):
    visited[A] = True
    current_path.append(A)


    if(A==B):
        #id(current_path)
        paths[time.time()] = current_path
    for neigh in links_dico[A]:
        if(not visited[neigh]):
            explore_all_paths_rec(neigh, B, links_dico, visited = visited, paths = paths, current_path = current_path.copy())

        else:
            #Here we use what has already been visited to see if we can simply extend the list
            exisiting_paths = list(paths.values())
            for path in exisiting_paths:
                if(neigh in path):
                    index = path.index(neigh)
                    create_new_path = True#This condition is to avoid crating infinite paths due to cycles
                    for node in path[index:]:
                        if(node in current_path):
                            create_new_path = False
                    if(create_new_path):
                        new_path = current_path+path[index:]
                        if(new_path not in exisiting_paths):
                            exisiting_paths.append(new_path)
                            paths[time.time()] = new_path
    if(paths!={}):
        return True, list(paths.values())
    else:
        return False, []

def explore_all_paths(A, B, all_nodes, links_dico):
    visited, paths = {}, {}
    current_path = []
    for n in all_nodes:
        visited[n] = False
    exists, paths = explore_all_paths_rec(A, B, links_dico, visited.copy(), paths, current_path.copy())

    #Remove the artificial operations
    #for path in paths:
    #    for n in path:
    #        if(n.get_type()=="Operation"):
    #            if(n.get_artificial_status()):
    #                path.remove(n)

    return exists, paths
    
