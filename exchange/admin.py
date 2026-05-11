from django.contrib import admin
from .models import Category, Complaint, DemoProfile, ExchangeRequest, Listing, ListingImage, Review


admin.site.site_header = 'Администрирование BarterExchange'
admin.site.site_title = 'Админка BarterExchange'
admin.site.index_title = 'Управление проектом'


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 0


@admin.register(DemoProfile)
class DemoProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating')
    search_fields = ('name', 'city')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'desired_category', 'city', 'status')
    list_filter = ('status', 'category', 'condition', 'city')
    search_fields = ('title', 'description', 'desired_keywords', 'owner__name')
    inlines = [ListingImageInline]


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ('offered_listing', 'requested_listing', 'initiator', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('offered_listing__title', 'requested_listing__title', 'initiator__name', 'receiver__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'target', 'score', 'exchange', 'created_at')
    list_filter = ('score',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'target', 'reporter', 'reason', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = (
        'reporter__name',
        'listing__title',
        'listing__owner__name',
        'target_profile__name',
        'comment',
        'resolution',
    )
    readonly_fields = ('created_at', 'updated_at')
    actions = ('mark_in_review', 'mark_resolved', 'mark_rejected', 'block_related_listings')

    @admin.display(description='Объект жалобы')
    def target(self, obj):
        return obj.listing or obj.target_profile

    @admin.action(description='Отметить: на рассмотрении')
    def mark_in_review(self, request, queryset):
        queryset.update(status=Complaint.Status.IN_REVIEW)

    @admin.action(description='Отметить: рассмотрена')
    def mark_resolved(self, request, queryset):
        queryset.update(status=Complaint.Status.RESOLVED)

    @admin.action(description='Отметить: отклонена')
    def mark_rejected(self, request, queryset):
        queryset.update(status=Complaint.Status.REJECTED)

    @admin.action(description='Заблокировать связанные объявления')
    def block_related_listings(self, request, queryset):
        listing_ids = queryset.exclude(listing__isnull=True).values_list('listing_id', flat=True)
        Listing.objects.filter(pk__in=listing_ids).update(status=Listing.Status.BLOCKED)
