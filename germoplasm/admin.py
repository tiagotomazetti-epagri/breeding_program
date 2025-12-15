# Imports do Django
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from .models import (
    DiseaseReaction, 
    GeneticMaterial,
    GeneticMaterialPhoto,
    Location,
    Marker,
    PhenologicalEvent,
    PhenologyObservation,
    Population,
    S_Allele,
)
from .forms import MutationCreationForm
from . import services

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

class DiseaseReactionInline(admin.TabularInline):
    model = DiseaseReaction
    extra = 0
    verbose_name = "Reação a Doença"
    verbose_name_plural = "Reações a Doenças"

class GeneticMaterialPhotoInline(admin.TabularInline):
    model = GeneticMaterialPhoto
    extra = 1
    fields = ('image', 'caption')
    verbose_name = "Foto"
    verbose_name_plural = "Fotos"

class GeneticMaterialForSAllelesInline(admin.TabularInline):
    model = GeneticMaterial.s_alleles.through
    extra = 0
    verbose_name = "Material Genético com este Alelo"
    verbose_name_plural = "Materiais Genéticos com este Alelo"
    fields = ('geneticmaterial',)
    readonly_fields = ('geneticmaterial',)
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

class MutationsInline(admin.TabularInline):
    """
    Inline para mostrar as mutações originadas a partir deste material.
    """
    model = GeneticMaterial
    fk_name = 'mutated_from'

    fields = ('name', 'material_type', 'get_display_code', 'observations')
    readonly_fields = ('name', 'material_type', 'get_display_code', 'observations')

    verbose_name = "Mutação Gerada"
    verbose_name_plural = "Mutações Geradas a Partir deste Material"

    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

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

# --- Configurações do Admin ---

@admin.register(GeneticMaterial)
class GeneticMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_display_code', 'material_type', 'is_active')
    list_filter = ('material_type', 'is_active', 'is_epagri_material')
    search_fields = ('name', 'internal_code', 'accession_code')
    autocomplete_fields = ('mother', 'father', 'population', 's_alleles')
    
    inlines = [
        GeneticMaterialPhotoInline,
        PhenologyObservationInline, 
        DiseaseReactionInline,
        ChildrenAsMotherInline,
        ChildrenAsFatherInline,
        MutationsInline
    ]
    
    actions = ['create_mutation_action', promote_to_selection, promote_to_cultivar]

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
                "</ul>"
                "<p>O sistema validará os dados e não permitirá combinações inválidas.</p>"
            ),
            'fields': ('population', 'mother', 'father')
        }),
        ('Genotipagem', {
            'fields': ('s_alleles',)
        }),
        ('Outras Informações', {
            'fields': ('observations',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ('internal_code', 'accession_code')

    def get_urls(self):
        """
        Adiciona as URLs customizadas para o fluxo da criação de mutação.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/create-mutation',
                self.admin_site.admin_view(self.create_mutation_form_view),
                name='germoplasm_geneticmaterial_createmutation',
            ),
        ]
        return custom_urls + urls
    
    def create_mutation_action(self, request, queryset):
        """Ação do Admin que inicia o fluxo de criação de mutação."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Por favor, selecione exatamente um material para criar uma mutação.",
                level=messages.WARNING
            )
            return None
        
        origin_material = queryset.first()
        return HttpResponseRedirect(
            reverse(
                "admin:germoplasm_geneticmaterial_createmutation",
                args=[origin_material.pk]
            )
        )
    
    create_mutation_action.short_description = "Cadastrar mutação a partir do material selecionado"

    def create_mutation_form_view(self, request, object_id):
        """
        View que exibe o formulário para inserir os dados do novo mutante.
        """
        origin_material = self.get_object(request, object_id)

        if request.method == 'POST':
            form = MutationCreationForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        mutation_count = GeneticMaterial.objects.filter(mutated_from=origin_material).count()
                        next_mutation_num = mutation_count + 1
                        
                        origin_code = origin_material.get_display_code()
                        new_mutation_code = f"{origin_code}M{next_mutation_num}"

                        new_mutant = GeneticMaterial()
                        new_mutant.material_type = origin_material.material_type
                        new_mutant.is_active = origin_material.is_active
                        new_mutant.pk = None
                        new_mutant._state.adding = True

                        new_mutant.name = form.cleaned_data['new_name']
                        
                        new_mutant.mutated_from = origin_material
                        
                        new_mutant.accession_code = new_mutation_code
                        
                        new_mutant.internal_code = None
                        new_mutant.population = None
                        new_mutant.mother = None
                        new_mutant.father = None
                        
                        mutant_char_text = f"CARACTERE MUTANTE: {form.cleaned_data['mutant_character']}"
                        original_obs = origin_material.observations or ""
                        if original_obs:
                            new_mutant.observations = f"{mutant_char_text}\n\n---\n\n{original_obs}"
                        else:
                            new_mutant.observations = mutant_char_text

                        new_mutant.save()

                        for reaction in origin_material.disease_reactions.all():
                            reaction.pk = None
                            reaction.genetic_material = new_mutant
                            reaction.save()
                        
                        for obs in origin_material.phenology_observations.all():
                            obs.pk = None
                            obs.genetic_material = new_mutant
                            obs.save()

                    self.message_user(
                        request,
                        f"Mutante '{new_mutant.name}' com código '{new_mutation_code}' criado com sucesso.",
                        level=messages.SUCCESS
                    )
                    return redirect(reverse('admin:germoplasm_geneticmaterial_changelist'))

                except Exception as e:
                    self.message_user(
                        request,
                        f"Ocorreu um erro ao criar a mutação: {e}",
                        level=messages.ERROR
                    )
                    return redirect(reverse('admin:germoplasm_geneticmaterial_changelist'))
        else:
            form = MutationCreationForm()

        context = {
            **self.admin_site.each_context(request),
            'title': f"Cadastrar Mutação de '{origin_material.name}'",
            'form': form,
            'opts': self.model._meta,
            'origin_material': origin_material,
        }
        return render(request, 'admin/germoplasm/create_mutation_form.html', context)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'city', 'state')

@admin.register(Marker)
class MarkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'marker_type')
    search_fields = ('name',)

@admin.register(PhenologicalEvent)
class PhenologicalEventAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(PhenologyObservation)
class PhenologyObservationAdmin(admin.ModelAdmin):
    list_display = ('genetic_material', 'event', 'location', 'observation_date')
    search_fields = ('genetic_material__name', 'event__name', 'location__name')
    autocomplete_fields = ('genetic_material', 'location', 'event')

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

@admin.register(S_Allele)
class S_AlleleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ('markers',)
    inlines = [GeneticMaterialForSAllelesInline]
