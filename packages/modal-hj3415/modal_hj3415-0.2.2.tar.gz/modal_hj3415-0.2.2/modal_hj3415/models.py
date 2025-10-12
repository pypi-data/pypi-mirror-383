from django.db import models

class BaseModal(models.Model):
    modal_title = models.CharField('modal_title', default="EVENT", max_length=50, blank=True)
    activate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-id",)  # 최신 우선

class ModalSingleBG(BaseModal):
    h3 = models.CharField('h3', max_length=50, help_text="강조 : strong tag")
    h1 = models.CharField('h1', max_length=100)
    h2 = models.TextField('h2', help_text="줄넘기기 : br tag, 강조 : strong tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    bg = models.ImageField(upload_to=f'images/modal_single_bg', null=True, blank=True)
    def __str__(self):
        return self.h1

    class Meta:
        verbose_name = "단일배경 팝업창"
        verbose_name_plural = "단일배경 팝업창 목록"

class ModalImageOnly(BaseModal):
    img = models.ImageField(upload_to=f'images/modal_image_only')

    def __str__(self):
        return self.modal_title

    class Meta:
        verbose_name = "이미지 팝업창"
        verbose_name_plural = "이미지 팝업창 목록"

class ModalLinkVideo(BaseModal):
    h2 = models.CharField('h2', max_length=100)
    p = models.TextField('p', help_text="줄넘기기 : br tag, 강조 : strong tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    link_video_url = models.CharField('link_video_url', blank=True, help_text="공란 가능", max_length=1200)
    link_video_text = models.CharField('link_video_text', default="Watch Video", max_length=50)
    bg = models.ImageField(upload_to=f'images/modal_link_video', blank=True, null=True)

    def __str__(self):
        return self.h2

    class Meta:
        verbose_name = "비디오링크 팝업창"
        verbose_name_plural = "비디오링크 팝업창 목록"


class ModalRotateBG(BaseModal):
    h2 = models.CharField('h2', max_length=100, help_text="줄넘기기 : br tag, 강조 : span tag")
    p = models.TextField('p', help_text="줄넘기기 : br tag")
    link_url = models.CharField('link_url', blank=True, help_text="공란 가능", max_length=1200)
    link_text = models.CharField('link_text', default="Get Started", max_length=50)
    bg = models.ImageField(upload_to=f'images/modal_rotate_bg', blank=True, null=True)
    bg2 = models.ImageField(blank=True, upload_to=f'images/modal_rotate_bg')
    bg3 = models.ImageField(blank=True, upload_to=f'images/modal_rotate_bg')

    def __str__(self):
        return self.h2

    class Meta:
        verbose_name = "순환배경 팝업창"
        verbose_name_plural = "순환배경 팝업창 목록"