# -*- coding: utf-8 -*-
from tagging.models import TaggedItem, Tag
from treemap.models import Tree
from treemap.lib.map_feature import context_dict_for_plot
import json
import re

def context_dict_for_tree(request, tree):
    tag_dict = {
        "id": tree.id,
    }
    return tag_dict

def context_dict_for_tag(request, tag):
    tag_dict = {
        "name": tag.tag.name,
    }
    return tag_dict

def context_dict_for_tags(request, tags, **kwargs):

    instance = request.instance
    user = request.user
    context = [context_dict_for_tag(request,tag)
                        for tag in tags]

    return context

def context_dict_for_tag_list(request, tag):
    return tag.tag.name,

def context_dict_for_tags_list(request, tags, **kwargs):

    instance = request.instance
    user = request.user
    context = [context_dict_for_tag_list(request,tag)
                        for tag in tags]
    context.sort()
    tags = ''
    for tag in context:
        tags += str(tag[0]) + ' '

    return tags.strip()

def get_tags_by_plot_id(request, instance, plot_id):
    tree = Tree.objects.get(plot_id=plot_id)
    tree_dict = context_dict_for_tree(request, tree)
    tag_list = context_dict_for_tags_list(request, TaggedItem.objects.filter(object_id=tree_dict['id']))
    return tag_list

def get_related_tags(request, instance, plot_id):    
    tree = Tree.objects.get(plot_id=plot_id)
    tree_dict = context_dict_for_tree(request, tree)
    related_trees_result = Tree.tagged.related_to(tree)

    related_trees = []
    for related_tree in related_trees_result:
        tree_dict = context_dict_for_tree(request, related_tree)
        related_trees.append({ "tree_id": tree_dict['id']})
    return {"related_trees": related_trees}

def create_tag(request, instance, plot_id):
    request_dict = json.loads(request.body)
    tree = Tree.objects.get(plot_id=plot_id)
    tree_dict = context_dict_for_tree(request, tree)
    Tag.objects.add_tag(tree, request_dict['name'])
    return request_dict['name'] #context_dict_for_tags_list(request, TaggedItem.objects.filter(object_id=tree_dict['id']))


def remove_tag(request, instance, plot_id, tag):
    tree = Tree.objects.get(plot_id=plot_id)
    tree_dict = context_dict_for_tree(request, tree)
    tag_list = context_dict_for_tags_list(request, TaggedItem.objects.filter(object_id=tree_dict['id']))
    strset = set(tag_list.split())
    tagset = set(tag.split())
    diffset = strset - tagset
    truncated_tags = ' '.join(diffset)    
    Tag.objects.update_tags(tree, truncated_tags)
    return tag #truncated_tags