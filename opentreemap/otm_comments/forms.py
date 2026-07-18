# -*- coding: utf-8 -*-


from threadedcomments.forms import ThreadedCommentForm

from otm_comments.models import EnhancedThreadedComment


class EnhancedThreadedCommentForm(ThreadedCommentForm):
    @staticmethod
    def get_comment_model(*args, **kwargs):
        return EnhancedThreadedComment
