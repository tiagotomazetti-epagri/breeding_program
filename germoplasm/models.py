import os
import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify

def genetic_material_photo_path(instance, filename):
    """
    Gera um caminho de arquivo limpo e único usando o nome do material.
    Exemplo: genetic_material_photos/gala-fuji/gala-fuji_a8b1.jpg
    """
    genetic_material = instance.genetic_material

    ext = os.path.splitext(filename)[1]
    safe_name = slugify(genetic_material.name)
    unique_suffix = uuid.uuid4().hex[:8]
    new_filename = f"{safe_name}_{unique_suffix}{ext}"
    return os.path.join('genetic_material_photos', str(genetic_material.id), new_filename)

class BaseMaterial(models.Model):
    """
    Abstract base model containing common fields for all material-related models.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo?",
        help_text="Marque se o material está ativo. Desmarque para exclusão lógica."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Data de Criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name="Última Atualização"
    )

    class Meta:
        abstract = True

class Marker(BaseMaterial):
    """
    Represents a molecular marker used for identification.
    """
    class MarkerType(models.TextChoices):
        SSR = 'SSR', 'SSR (Microssatélite)'
        SNP = 'SNP', 'SNP'
        CAPS = 'CAPS', 'CAPS'
        OTHER = 'OTHER', 'Outro'
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome do Marcador"
    )
    marker_type = models.CharField(
        max_length=10,
        choices=MarkerType.choices,
        verbose_name="Tipo de Marcador"
    )
    primer_forward = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Primer Forward"
    )
    primer_reverse = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Primer Reverse"
    )
    pcr_protocol = models.TextField(
        blank=True,
        verbose_name="Protocolo de PCR"
    )

    def __str__(self):
        verbose_name = "Marcador Molecular"
        verbose_name_plural = "Marcadores Moleculares"

class S_Allele(BaseMaterial):
    """
    Represents an S-allele for self-incompatibility
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome do Alelo S",
        help_text="Ex: S1, S2, S3, S9"
    )
    markers = models.ManyToManyField(
        Marker,
        blank=True,
        related_name="s_alleles",
        verbose_name="Marcadores para Identificação"
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Alelo S"
        verbose_name_plural = "Alelos S"
        ordering = ["name"]

class GeneticMaterial(BaseMaterial):
    """
    Represents a genetic material in the Germplasm Active Bank (BAG).
    """
    class MaterialType(models.TextChoices):
        CULTIVAR = 'CULTIVAR', 'Cultivar'
        SELECTION = 'SELECTION', 'Seleção'
        HYBRID = 'HYBRID', 'Híbrido'
    
    name = models.CharField(
        max_length=255,
        verbose_name="Nome / Designação",
        help_text="Nome comercial ou designação do material (ex. Gala, Fuji, M5)."
    )
    material_type = models.CharField(
        max_length=10,
        choices=MaterialType.choices,
        verbose_name="Tipo de Material"
    )
    internal_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Código Interno",
        help_text="Código sequencial gerado para linhagens e cultivares (ex: L1, C5)."
    )
    accession_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        verbose_name="Código de Acesso (Híbrido)",
        help_text="Código gerado para Híbridos e mantido em suas evoluções (ex. C1xL5A25H1)."
    )

    mother = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children_as_mother',
        verbose_name="Parental (Mãe)"
    )

    father = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children_as_father',
        verbose_name="Parental (Pai)"
    )

    is_epagri_material = models.BooleanField(
        default=False,
        verbose_name="É material do programa da Epagri?",
        help_text="Marque esta opção se o material foi gerado a partir de uma população do programa" \
        " de melhoramento genético da EPAGRI."
    )
    
    population = models.ForeignKey(
        'Population',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_hybrids',
        verbose_name="População de Origem"
    )

    mutated_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mutations",
        verbose_name="Mudatão de",
        help_text="Selecione o material genético original se este for uma mutação."
    )

    s_alleles = models.ManyToManyField(
        S_Allele,
        blank=True,
        related_name="genetic_materials",
        verbose_name="Genótipo S (Alelos S)",
        help_text="Selecione os alelos S que compõem o genótipo deste material"
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Utilize este campo se necessário para adicionar informações uteis sobre o genótipo."
    )

    ifo_sent = models.BooleanField(
        default=False,
        verbose_name="Envio para IFO",
        help_text="Marque se este material foi enviado para a IFO."
    )

    ifo_sent_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Envio para a IFO"
    )

    ifo_quarantine_released = models.BooleanField(
        default=False,
        verbose_name="Liberação da Quarentena IFO"
    )

    ifo_discarded = models.BooleanField(
        default=False,
        verbose_name="Descarte no IFO",
        help_text="Marque se o material foi descartado durante o processo na IFO."
    )

    ifo_discarded_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Descarte no IFO"
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.get_display_code()})"
    
    def get_display_code(self) -> str:
        if self.material_type == self.MaterialType.HYBRID:
            return self.accession_code or self.name
        return self.internal_code or self.name
    
    def _clean_register(self) -> None:
            # Conta quantos tipos de origem foram preenchidos
            origins = [
                bool(self.population),
                bool(self.mother or self.father),
                bool(self.mutated_from)
            ]
            
            # A função sum() em uma lista de booleanos conta quantos 'True' existem.
            if sum(origins) > 1:
                raise ValidationError(
                    "Conflito de Genealogia: Preencha apenas um tipo de origem. "
                    "Escolha entre 'População', 'Parentais (Mãe/Pai)' ou 'Mutação de', mas não os combine."
                )

            # Validação de Auto-referência
            if self.pk:
                if self.mother_id == self.pk or self.father_id == self.pk or self.mutated_from_id == self.pk:
                    raise ValidationError("Um material não pode ser seu próprio parental ou origem de mutação.")
                
    def _clean_update(self) -> None:
        if self.population:
            if (
                self.mother_id != self.population.parent1_id or
                self.father_id != self.population.parent2_id
            ):
                raise ValidationError(
                "Conflito na Edição: Os parentais (Mãe/Pai) não correspondem à População de Origem Selecionada. "
                "Para materiais do programa, a genealogia é definida pela população e não deve ser alterada manualmente"
            )

    def clean(self):
        super().clean()

        if not self.pk:
            self._clean_register()
        else:
            self._clean_update()

    def save(self, *args, **kwargs):
        """
        Garante que a genealogia e os códigos sejam salvos corretamente.
        """
        # Define 'is_epagri_material' com base na única condição possível:
        # se uma população foi fornecida.
        if self.population:
            self.is_epagri_material = True
            self.mother = self.population.parent1
            self.father = self.population.parent2
        else:
            # Se não há população, garantimos que o material não seja classificado como do programa.
            self.is_epagri_material = False

        # Lógica de geração de código (mantendo a sua versão simplificada)
        is_new = self._state.adding
        super().save(*args, **kwargs) # Salva primeiro para obter um ID.

        if is_new and not self.internal_code:
            code_to_set = None
            if self.material_type == self.MaterialType.CULTIVAR:
                code_to_set = f'C{self.id}'
            elif self.material_type == self.MaterialType.SELECTION:
                code_to_set = f'S{self.id}'
            
            if code_to_set:
                GeneticMaterial.objects.filter(pk=self.pk).update(internal_code=code_to_set)
                self.internal_code = code_to_set
    
    class Meta:
        verbose_name = "Material Genético"
        verbose_name_plural = "Materiais Genéticos (BAG)"
        ordering = ['name']

class DiseaseReaction(BaseMaterial):
    """
    Records the reaction of a genetic material to a specific disease.
    """
    class ReactionLevel(models.TextChoices):
        RESISTANT = 'R', 'Resistente'
        MODERATELY_RESISTANT = 'MR', 'Moderadamente Resistente'
        MODERATELY_SUSCEPTIBLE = 'MS', 'Moderadamente Suscetível'
        SUSCEPTIBLE = 'S', 'Suscetível'
    
    genetic_material = models.ForeignKey(
        GeneticMaterial,
        on_delete=models.CASCADE,
        related_name='disease_reactions',
        verbose_name="Material Genético"
    )
    disease_name = models.CharField(
        max_length=255,
        verbose_name="Nome da Doença"
    )
    reaction = models.CharField(
        max_length=2,
        choices=ReactionLevel.choices,
        blank=True,
        verbose_name="Reação"
    )

    def __str__(self) -> str:
        return f"{self.genetic_material.name} - {self.disease_name}: {self.get_reaction_display()}"
    
    class Meta:
        verbose_name = "Reação a Doença"
        verbose_name_plural = "Reações a Doenças"
        constraints = [
            models.UniqueConstraint(
                fields=['genetic_material', 'disease_name'],
                name='unique_reaction_per_material_disease'
            )
        ]

class GeneticMaterialPhoto(BaseMaterial):
    """
    Representa uma única foto associada a um GeneticMaterial
    """
    genetic_material = models.ForeignKey(
        GeneticMaterial,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Material Genético",    
    )
    image = models.ImageField(
        upload_to=genetic_material_photo_path,
        verbose_name="Imagem"
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Legenda",
        help_text="Descrição opcional da foto (ex: 'Fruto em ponto de colheita')."
    )

    def __str__(self):
        return f"Foto de {self.genetic_material.name}"

    class Meta:
        verbose_name = "Foto de Material Genético"
        verbose_name_plural = "Fotos de Materiais Genéticos"

class Location(models.Model):
    """Represents a physical location for phenological observations."""
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome do Local")
    city = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    state = models.CharField(max_length=100, blank=True, verbose_name="Estado")

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude"
    )
    altitude = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altitude (metros)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locais"

class PhenologicalEvent(models.Model):
    """Represents a type of phenological event (e.g., Budding, Flowering)."""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Nome do Evento"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Evento Fenológico"
        verbose_name_plural = "Eventos Fenológicos"

class PhenologyObservation(BaseMaterial):
    """Records a specific phenological observation for a genetic material."""
    genetic_material = models.ForeignKey(
        GeneticMaterial,
        on_delete=models.CASCADE,
        related_name='phenology_observations',
        verbose_name="Material Genético"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name="Local da Observação"
    )
    event = models.ForeignKey(
        PhenologicalEvent,
        on_delete=models.PROTECT,
        verbose_name="Evento Fenológico"
    )
    observation_date = models.DateField(
        default=timezone.now,
        verbose_name="Data da Observação"
    )

    def __str__(self):
        return f"{self.genetic_material.name} - {self.event.name} em {self.observation_date.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Observação Fenológica"
        verbose_name_plural = "Observações Fenológicas"
        ordering = ['-observation_date']

class Planting(BaseMaterial):
    """
    Represents a specific planting of a GeneticMaterial at a Location.
    """
    genetic_material = models.ForeignKey(
        'GeneticMaterial',
        on_delete=models.CASCADE,
        related_name='plantings',
        verbose_name="Material Genético"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name="Local de Plantio"
    )
    num_plants = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Plantas"
    )
    planting_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Plantio"
    )
    rootstock = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Porta-enxerto"
    )

    def __str__(self):
        return f"{self.num_plants} Planta(s) de {self.genetic_material.name} em {self.location.name}."
    
    class Meta:
        verbose_name = "Local de Plantio"
        verbose_name_plural = "Locais de Plantio (Onde tem)"
        ordering = ['location', '-planting_date']

class Population(BaseMaterial):
    """
    Represents a population created from a cross between two genetic materials.
    """
    code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        editable=False,
        verbose_name="Código da População"
    )
    seplan_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        editable=True,
        verbose_name="Códio do projeto no Seplan"
    )
    parent1 = models.ForeignKey(
        GeneticMaterial,
        on_delete=models.PROTECT,
        related_name='population_as_parent1',
        verbose_name="Parental 1"
    )
    parent2 = models.ForeignKey(
        GeneticMaterial,
        on_delete=models.PROTECT,
        related_name='population_as_parent2',
        verbose_name="Parental 2"
    )
    cross_date = models.DateField(
        default=timezone.now,
        verbose_name="Data do Cruzamento"
    )
    flowers_quantity = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Quantidade de flores polinizadas",
        help_text="Número total de flores emasculadas e polinizadas para esta população."
    )
    fruit_quantity = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Quantidade de frutos gerados",
        help_text="Número total de frutos gerados a partir das flores polinizadas."
    )
    seed_quantity = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Quantidade de sementes coletadas",
        help_text="Número total de sementes coletadas a partir dos frutos obtidos no cruzamento"
    )
    greenhouse_seedling_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade de Seedlings na estufa",
        help_text="Número total de seedlings gerados nesta população."
    )
    field_seedling_quantity = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Quantidade de seedlings a campo",
        help_text="Número total de seedlings que foram transplantados a campo"
    )
    observations = models.TextField(
        blank=True,
        verbose_name="Observações"
    )

    def __str__(self) -> str:
        return self.code or f"Cruzamento de {self.parent1.name} x {self.parent2.name}"
    
    def clean(self):
        if not self.parent1_id or not self.parent2_id:
            raise ValidationError(
                "Os parentais devem ser selecionados e salvos antes de criar uma população."
            )

    def save(self, *args, **kwargs) -> None:
        if not self.code:
            self.full_clean()
            year_suffix = self.cross_date.strftime('%y')
            p1_code = self.parent1.get_display_code()
            p2_code = self.parent2.get_display_code()
            self.code = f"{p1_code}X{p2_code}A{year_suffix}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "População"
        verbose_name_plural = "Populações"
        ordering = ['-cross_date']
