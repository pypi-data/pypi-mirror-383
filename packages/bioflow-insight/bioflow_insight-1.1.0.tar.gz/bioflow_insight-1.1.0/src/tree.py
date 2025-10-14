class Tree:
    def __init__(self, value, conditions, children):
        self.value = value
        self.conditions = conditions
        self.children = children

    def is_this_full_tree(self):
        return self.value==None and self.conditions==[]
    

    def create_copy(self):
        t = Tree(value=self.value, conditions=self.conditions, children=[])
        if(not self.is_a_leaf()):
            for c in self.children:
                t.children.append(c.create_copy())
        return t
            
    
    def is_a_leaf(self):
        return self.children==[] 
    
    #This method returns all the children in the immediate depth 
    #And if a child is a tree it returns all the recursive children of that tree
    def get_shallow_children(self):
        tab = []
        for child in self.children:
            leafs = child.get_all_leafs_in_tree(val={})
            if(leafs!=[]):
                tab.append(leafs)
        return tab
    
    def add_child(self, child):
        self.children.append(child)

    def add_children(self, cluster):
        for c in cluster:
            temp = Tree(value=c, conditions=[], children = [])
            self.add_child(temp)

    def get_all_leafs_in_tree(self, val):
        if(self.is_a_leaf()):#and type(self.value)!=str):
            val[self.value] = ""
        for child in self.children:
            child.get_all_leafs_in_tree(val)
        return list(val.keys())
    
    #Transfers the tree's children to self
    def transfer_children(self, tree):
        for i in range(len(tree.children)):
            self.children.append(tree.children[i])

    def get_conditions(self):
        return self.conditions
    
    def get_children(self):
        return self.children
    
    def get_conditions_in_commun(self, tree):
        return list(set(self.get_conditions()).intersection(tree.get_conditions()))


    def add_conditions_to_tree(self, node_2_conditions):
        if(self.is_a_leaf()):
            try:
                self.conditions = node_2_conditions[self.value]
            except:
                self.conditions = []
        else:
            conditions_in_common = []
            for child in self.children:
                child.add_conditions_to_tree(node_2_conditions)
                conditions_in_common.append(child.get_conditions())
            self.conditions = list(set.intersection(*map(set, conditions_in_common)))



    def get_value_conditions(self):
        try:
            return self.conditions
        except:
            return None



    def fill_tree(self, tree, parent_id):
        tree.create_node(get_val(self.value),  id(self), parent=parent_id)
        for child in self.children:
            child.fill_tree(tree, id(self))
        
    def merge_2_children_together(self, child1, child2, groups_created):

        G1, G2 = child1.get_all_leafs_in_tree({}), child2.get_all_leafs_in_tree({})
        #print(G1, G2)
        #print(child1.value, child2.value)
        #print(child1.is_a_leaf(), child2.is_a_leaf())
        #print(child1.children, child2.children)
        new_value = f"G{groups_created}"
        new_child = Tree(value=new_value, conditions = [], children=[])
        #Transfer all the children of child2 to child1
        if(child2.is_a_leaf()):
            if(child1.is_a_leaf()):                
                #print("child1 is a leaf and child2 is a leaf")
                new_child.add_children(G1+G2)
            else:
                #print("child1 is NOT a leaf and child2 is a leaf")
                new_child.transfer_children(child1)
                new_child.add_children(G2)

        else:
            if(child1.is_a_leaf()):
                #print("child1 is a leaf and child2 is NOT a leaf")
                new_child.transfer_children(child2)
                new_child.add_children(G1)
            else:
                #print("child1 is NOT a leaf and child2 is NOT a leaf")
                new_child.transfer_children(child2)
                new_child.transfer_children(child1)

        
        self.children.remove(child1)
        self.children.remove(child2)
        self.children.append(new_child)


    def get_number_of_groups(self, num):
        for child in self.children:
            if(not child.is_a_leaf()):
                num = child.get_number_of_groups(num+1)
        return num
    
    def get_size_of_groups(self, tab):
        for child in self.children:
            if(not child.is_a_leaf()):
                tab.append(len(child.children))
                tab = child.get_size_of_groups(tab)
        return tab
    
    #This is the percentage of nodes which are in a group
    def get_coverage(self):
        if(self.children!=[]):
            nb_swallow_leafs = 0
            for child in self.children:
                if(child.is_a_leaf()):
                    nb_swallow_leafs+=1
            nb_leafs = len(self.get_all_leafs_in_tree({}))
            return (nb_leafs-nb_swallow_leafs)/nb_leafs*100
        return 0
    
    #This is the percentage of processes which are in a group
    def get_coverage_processes(self):
        if(self.children!=[]):
            nb_swallow_leafs = 0
            for child in self.children:
                if(child.is_a_leaf() and child.value.get_type()=="Process"):
                    nb_swallow_leafs+=1
            if(nb_swallow_leafs==0):
                return 0
            total = 0
            for leaf in self.get_all_leafs_in_tree({}):
                if(leaf.get_type()=="Process"):
                    total+=1
            return (total-nb_swallow_leafs)/total*100
        return 0

    def show_tree(self):
        from treelib import Node, Tree
        tree = Tree()
        tree.create_node("Root", "root")
        for child in self.children:
            child.fill_tree(tree, "root")
        tree.show()

    def remove_clouds(self):
        to_remove, to_add= [], []
        for child in self.children:
            if(child.is_a_leaf() and child.value.get_type()=="Cloud"):
                operations = child.value.get_operations()
                for o in operations:
                    to_add.append(Tree(value=o, conditions=child.conditions, children=[]))
                to_remove.append(child)
            else:
                child.remove_clouds()
        for r in to_remove:
            self.children.remove(r)
        self.children+=to_add
            
                


def get_val(node):
    try:
        if(node.get_type()=="Process"):
            return node.get_name()
        elif(node.get_type()=="Operation"):
            return node.get_code(get_OG = True)
        elif(node.get_type()=="Cloud"):
            return "Cloud"
    except:
        return node
