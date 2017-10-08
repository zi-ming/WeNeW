
from django.conf.urls import url

from Subpage import views

urlpatterns = [
    url(r'^$', views.parse2Website, name="parse2Website"),
    url(r'^parse2Content', views.parse2Content, name="parse2content"),
    url(r'^saveWebsiteXpath$', views.saveWebsiteXpath, name="savewebsitexpath"),
    url(r'^websiteSub/$', views.websiteSub, name="websiteSub"),
    url(r'^contentSub/$', views.contentSub, name="contentSub"),
    url(r'^iframe_contentPage$', views.iframe_contentPage, name="iframe_contentPage"),
    url(r'^iframe_previewPage$', views.iframe_previewPage, name="iframe_previewPage"),
    url(r'^sub_manager$', views.sub_manager, name="sub_manager"),
    url(r'^website_msg$', views.website_msg, name="website_msg"),
]
