# Imports do Django
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Max
from django.template.loader import render_to_string

# Imports locais
from .models import (
    DiseaseReaction, 
    GeneticMaterial,
    GeneticMaterialPhoto,
    Location,
    PhenologicalEvent,
    PhenologyObservation,
    Population,
)
from . import services

class GeneticMaterialPhotoInline(admin.TabularInline):
    model = GeneticMaterialPhoto
    extra = 1
    fields = ('image', 'caption')
    verbose_name = "Foto"
    verbose_name_plural = "Fotos"

class ChildrenAsMotherInline(admin.TabularInline):
    """Inline para mostrar os filhos onde o material é a mãe."""
    model = GeneticMaterial
    fk_name = 'mother'
    fields = ('name', 'material_type', 'get_display_code')
    readonly_fields = ('name', 'material_type', 'get_display_code')
    verbose_name = "Filho (como mãe)"
    verbose_name_plural = "Filhos (onde este material é a mãe)"
    can_delete = False
    extra = 0

class ChildrenAsFatherInline(admin.TabularInline):
    """Inline para mostrar os filhos onde o material é o pai."""
    model = GeneticMaterial
    fk_name = 'father'
    fields = ('name', 'material_type', 'get_display_code')
    readonly_fields = ('name', 'material_type', 'get_display_code')
    verbose_name = "Filho (como pai)"
    verbose_name_plural = "Filhos (onde este material é o pai)"
    can_delete = False
    extra = 0

class DiseaseReactionInline(admin.TabularInline):
    model = DiseaseReaction
    extra = 0
    verbose_name = "Reação a Doença"
    verbose_name_plural = "Reações a Doenças"

class PhenologyObservationInline(admin.TabularInline):
    model = PhenologyObservation
    extra = 0
    autocomplete_fields = ('location', 'event')
    verbose_name = "Observação Fenológica"
    verbose_name_plural = "Observações Fenológicas"
    

class SeplanSearchFilter(admin.SimpleListFilter):
    title = _('Código Seplan')
    parameter_name = 'seplan_search'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(
            request
        ).exclude(seplan_code__isnull=True).exclude(seplan_code__exact='')
        unique_codes = qs.values_list('seplan_code', flat=True).order_by('seplan_code').distinct()
        return [(code, f"Seplan {code}") for code in unique_codes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(seplan_code__exact=self.value())
        return queryset


@admin.action(description='Promover Híbrido(s) selecionado(s) para Seleção(ões)')
def promote_to_selection(modeladmin, request, queryset):
    updated_count = 0
    hybrids_to_promote = queryset.filter(material_type='HYBRID')

    if not hybrids_to_promote.exists():
        messages.warning(request, "Nenhum híbrido foi selecionado para promoção.")
        return None
    
    for hybrid in hybrids_to_promote:
        try:
            services.promote_hybrid_to_selection(hybrid)
            updated_count += 1
        except ValueError as e:
            messages.error(request, str(e))
    
    if updated_count > 0:
        messages.success(
            request,
            f"{updated_count} híbrido(s) foram promovidos para Seleção(ões) com sucesso."
        )
    else:
        messages.warning(
            request,
            "Nenhum híbrido válido foi selecionado para promoção."
        )


@admin.action(description='Promover Seleção(ões) para Cultivar(es)')
def promote_to_cultivar(modeladmin, request, queryset):
    updated_count = 0
    selections_to_promote = queryset.filter(material_type='SELECTION')

    if not selections_to_promote.exists():
        messages.warning(request, "Nenhuma Seleção foi selecionada para a promoção.")
        return None
    for selection in selections_to_promote:
        try:
            services.promote_selection_to_cultivar(selection)
            updated_count += 1
        except ValueError as e:
            messages.error(request, str(e))
            
    if updated_count > 0:
        messages.success(
            request,
            f"{updated_count} Seleção(ões) promovida(s) para Cultivar."
        )


# --- Configurações do Admin ---

@admin.register(GeneticMaterial)
class GeneticMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_display_code', 'material_type', 'is_active')
    list_filter = ('material_type', 'is_active', 'is_epagri_material')
    search_fields = ('name', 'internal_code', 'accession_code')
    autocomplete_fields = ('mother', 'father', 'population', 'mutated_from')
    
    inlines = [
        GeneticMaterialPhotoInline,
        PhenologyObservationInline, 
        DiseaseReactionInline,
        ChildrenAsMotherInline,
        ChildrenAsFatherInline
    ]
    
    actions = [promote_to_selection, promote_to_cultivar]

    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'material_type')
        }),
        ('Genealogia', {
            'description': (
                "<p><b>Instruções de Preenchimento:</b></p>"
                "<ul>"
                "<li><b>Para materiais do programa:</b> Preencha <u>apenas</u> o campo 'População de Origem'.</li>"
                "<li><b>Para materiais externos:</b> Preencha <u>apenas</u> os campos 'Parental (Mãe)' e/ou 'Parental (Pai)'.</li>"
                "<li><b>Para mutações:</b> Preencha <u>apenas</u> o campo 'Mutação de'.</li>"
                "</ul>"
                "<p>O sistema validará os dados e não permitirá combinações inválidas.</p>"
            ),
            'fields': ('population', 'mother', 'father', 'mutated_from')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ('internal_code', 'accession_code')


@admin.action(description='Selecionar Seedling(s) e promover para Híbrido')
def promote_seedling_to_hybrid(modeladmin, request, queryset):
    """
    Ação do Admin para criar um novo GeneticMaterial (Híbrido) a partir de uma população.
    """
    if queryset.count() != 1:
        messages.error(request, "Por favor, selecione exatamente uma população para esta ação.")
        return

    population = queryset.first()
    
    # 1. Encontra o próximo número sequencial para o híbrido nesta população
    last_hybrid = population.generated_hybrids.aggregate(
        max_accession=Max('accession_code')
    )
    
    next_num = 1
    if last_hybrid['max_accession']:
        try:
            # Extrai o número depois de 'H' (ex: C1xL5A25H1 -> 1)
            last_num_str = last_hybrid['max_accession'].split('H')[-1]
            next_num = int(last_num_str) + 1
        except (ValueError, IndexError):
            # Fallback caso o formato do código seja inesperado
            pass

    # 2. Gera o código e o nome do novo híbrido
    new_accession_code = f"{population.code}H{next_num}"
    
    # 3. Cria o novo material genético
    new_hybrid = GeneticMaterial.objects.create(
        name=new_accession_code, # Nome padrão
        material_type=GeneticMaterial.MaterialType.HYBRID,
        accession_code=new_accession_code,
        population=population,
        mother=population.parent1, # Assumindo parent1 como mãe, pode ser ajustado
        father=population.parent2, # Assumindo parent2 como pai
    )
    
    messages.success(
        request,
        f"Híbrido {new_hybrid.accession_code} criado com sucesso a partir da população {population.code}."
    )


@admin.register(Population)
class PopulationAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'seplan_code', 'parent1', 'parent2', 'cross_date', 
        'flowers_quantity', 'fruit_quantity', 'seed_quantity'
    )
    list_filter = ('cross_date', SeplanSearchFilter)
    search_fields = ('code', 'seplan_code')
    autocomplete_fields = ('parent1', 'parent2')
    readonly_fields = ('code',)
    actions = [promote_seedling_to_hybrid]

# Registrando os novos modelos no admin
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'city', 'state')

@admin.register(PhenologicalEvent)
class PhenologicalEventAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(PhenologyObservation)
class PhenologyObservationAdmin(admin.ModelAdmin):
    list_display = ('genetic_material', 'event', 'location', 'observation_date')
    search_fields = ('genetic_material__name', 'event__name', 'location__name')
    autocomplete_fields = ('genetic_material', 'location', 'event')
