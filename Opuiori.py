import pandas as pd

_supports={}
_itemsets=[]
_records=[]

def get_support(records,itemset=None):
    global _supports
    supports={}
    if itemset==None:
        for itemlist in records:
            for item in itemlist:
                if item == 'nan':
                    continue
                if (item,) in supports.keys():
                    supports[(item,)]=supports[(item,)]+1
                else:
                    supports[(item,)]=1
    else:
        for item in itemset:
            temp=set(item)
            for itemlist in records:
                tempset=set(itemlist)
                if temp.issubset(tempset):
                    if tuple(temp) in supports.keys():
                        supports[tuple(temp)]=supports[tuple(temp)]+1
                    else:
                        supports[tuple(temp)]=1
    for key in supports:
        supports[key]= supports[key]/len(records)
    _supports.update(supports)
    return supports


def total_support(item):
    global _records
    support=0
    temp=set(item)
    for itemlist in _records:
        tempset=set(itemlist)
        if temp.issubset(tempset):
            support=support+1
    return support/len(_records)

def eliminate(support,min_sup):
    current=[]
    for key in support:
        if support[key]>min_sup:
            current.append(key)
    return current

def union(tuple1,tuple2,k):
    if len(tuple1)==1:
        return (tuple1[0],tuple2[0])
    else:
        templist=list(tuple1) 
        for item in tuple2:
            if item not in templist:
                templist.append(item)
        if len(templist)>=(len(tuple1)+len(tuple2)-(k-2)):
            templist.sort()
            return tuple(templist)
        else:
            return None
        
def create_superset(itemlist,k):
    new_itemlist=[]
    for i in range(0,len(itemlist),1):
        for j in range(i+1,len(itemlist),1):
            new_item=union(itemlist[i],itemlist[j],k)
            if new_item is not None and new_item not in new_itemlist:
                new_itemlist.append(new_item)
    return new_itemlist

def create_subset (itemset):
    l=list(itemset)
    base = []   
    lists = [base] 
    for i in range(len(l)): 
        orig = lists[:] 
        new = l[i] 
        for j in range(len(lists)): 
            lists[j] = lists[j] + [new] 
        lists = orig + lists 
    rules=[]
    for anc in lists[1:-1]:
        con=[item for item in l if item not in anc]
        rules.append([tuple(con),tuple(anc)])
    return rules

def get_rules(current,supports,min_conf=0.5):
    ant=[]
    cons=[]
    conf=[]
    for item in current:
        rules = create_subset(item)
        for rule in rules:
            x=total_support(rule[0]+rule[1])
            y=total_support(rule[0])
            confidence=x/y
            if confidence>=min_conf:
                ant.append(rule[0])
                cons.append(rule[1])
                conf.append(confidence)
    df=pd.DataFrame({"antecedents":ant,"consequents":cons,"Confidence":conf})
    return df.drop_duplicates(subset=None, keep='first', inplace=False).reset_index()

def get_frequent_itemsets(itemsets,supports):
    itemset=[]
    support=[]
    for item in itemsets:
        itemset.append(item)
        support.append(supports[item])
    df=pd.DataFrame({"Frequent Itemsets":itemset,"Support":support})
    return df.drop_duplicates(subset=None, keep='first', inplace=False).reset_index()

def apriori(records,min_sup,min_conf):
    global _itemsets,_supports,_records
    _records=records
    _itemsets=[]
    _supports={}
    support = get_support(records)
    current=eliminate(support,min_sup)
    k=1
    while True:
        k=k+1
        _itemsets=_itemsets+current
        superset=create_superset(current,k)
        tempsupport=get_support(records,superset)
        temp=eliminate(tempsupport,min_sup)
        if len(temp)==0:
            break
        else:
            current = temp
            support=tempsupport
    frequent_itemsets=get_frequent_itemsets(_itemsets,_supports)
    rules= get_rules(_itemsets,_supports,min_conf)
    return frequent_itemsets,rules