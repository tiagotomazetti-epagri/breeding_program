from django.db import transaction
from .models import GeneticMaterial

@transaction.atomic
def promote_hybrid_to_selection(hybrid: GeneticMaterial) -> GeneticMaterial:
    """
    Promotes a HYBRID to a SELECTION.
    - Changes material_type to SELECTION.
    - Generates a new sequential internal_code (L-code).
    - Keeps the original accession_code for traceability.
    """
    if hybrid.material_type != GeneticMaterial.MaterialType.HYBRID:
        raise ValueError("Apenas materiais do tipo Híbrido podem ser promovidos para Seleção.")

    hybrid.material_type = GeneticMaterial.MaterialType.SELECTION
    
    # O método save() do modelo já cuida da geração do 'L-code'.
    # Precisamos chamar save() duas vezes se o código depende do ID.
    # No nosso caso, o save atualizado já lida com isso.
    hybrid.save()
    
    return hybrid

@transaction.atomic
def promote_selection_to_cultivar(selection: GeneticMaterial) -> GeneticMaterial:
    """
    Promotes a SELECTION to a CULTIVAR.
    - Changes material_type to CULTIVAR.
    - Generates a new sequential internal_code (C-code).
    - Keeps all previous codes for traceability.
    """
    if selection.material_type != GeneticMaterial.MaterialType.SELECTION:
        raise ValueError("Apenas materiais do tipo Seleção podem ser promovidos para Cultivar.")

    selection.material_type = GeneticMaterial.MaterialType.CULTIVAR
    
    selection.save()
    
    return selection
