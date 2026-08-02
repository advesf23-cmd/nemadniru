from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, DetailView, View

from .models import Post, BlogCategory, Tag, Comment


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        qs = Post.objects.filter(status="published").select_related("category", "author")
        category_slug = self.request.GET.get("category")
        tag = self.request.GET.get("tag")
        search_query = self.request.GET.get("q")
        sort = self.request.GET.get("sort", "newest")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if tag:
            qs = qs.filter(tags__name=tag)
        if search_query:
            qs = qs.filter(title__icontains=search_query)

        order_map = {"newest": "-published_at", "oldest": "published_at", "popular": "-views_count"}
        return qs.order_by(order_map.get(sort, "-published_at")).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = BlogCategory.objects.all()
        ctx["tags"] = Tag.objects.all()
        ctx["current_sort"] = self.request.GET.get("sort", "newest")
        return ctx

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
            html = render_to_string("blog/_post_grid.html", context, request=request)
            pagination_html = render_to_string("blog/_pagination.html", context, request=request)
            return JsonResponse({
                "html": html,
                "pagination": pagination_html,
                "count": context["paginator"].count,
            })
        return self.render_to_response(context)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(status="published")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=["views_count"])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related_posts"] = Post.objects.filter(
            category=self.object.category, status="published"
        ).exclude(pk=self.object.pk)[:3]
        ctx["comments"] = self.object.comments.filter(is_approved=True, parent__isnull=True).prefetch_related("replies")
        return ctx


class AddCommentView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, status="published")
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        text = request.POST.get("text", "").strip()
        parent_id = request.POST.get("parent_id")

        if full_name and text:
            Comment.objects.create(
                post=post, full_name=full_name, email=email, text=text,
                parent_id=parent_id or None,
            )
            messages.success(request, "نظر شما ثبت شد و پس از تأیید مدیر نمایش داده خواهد شد.")
        else:
            messages.error(request, "لطفاً نام و متن نظر را وارد کنید.")
        return redirect(reverse("blog:post_detail", kwargs={"slug": slug}) + "#comments")
