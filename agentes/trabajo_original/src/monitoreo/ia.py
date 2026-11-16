"""Módulo de Inteligencia Artificial Aislada para RutaSIT Arequipa (E5).

Aísla el componente de IA no determinista detrás de los patrones GoF:
- Strategy / Adapter: Interfaz IProveedorLLM y adaptador MockLLMAdapter (sustituible).
- Decorator: CacheIADecorator para evitar reconsultar el LLM ante prompts idénticos.
- Chain of Responsibility: Cadena de guardrails para validar que la respuesta no
  alucine datos contradictorios con la telemetría ni use lenguaje inadecuado.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict


class ViolacionGuardrailError(ValueError):
    """Excepción lanzada cuando una salida del LLM no supera los filtros de seguridad."""
    pass


@dataclass
class RespuestaIA:
    """Modelo canónico de respuesta generada por el proveedor de IA."""
    texto: str
    modelo: str
    tokens_utilizados: int = 0


# ==============================================================================
# Patrón Strategy / Adapter: Proveedor de LLM intercambiable
# ==============================================================================

class IProveedorLLM(ABC):
    """Puerto formal (Strategy/Target) para interactuar con modelos de lenguaje."""

    @abstractmethod
    def generar_explicacion(self, prompt: str) -> RespuestaIA:
        """Genera una explicación en lenguaje natural a partir de un prompt."""
        raise NotImplementedError


class MockLLMAdapter(IProveedorLLM):
    """Adaptador de pruebas que simula respuestas de un LLM sin llamadas a red ni API keys."""

    def __init__(self, respuesta_forzada: Optional[str] = None):
        self.respuesta_forzada = respuesta_forzada
        self.llamadas: int = 0

    def generar_explicacion(self, prompt: str) -> RespuestaIA:
        self.llamadas += 1
        if self.respuesta_forzada is not None:
            return RespuestaIA(texto=self.respuesta_forzada, modelo="mock-llm-v1", tokens_utilizados=25)

        prompt_lower = prompt.lower()
        import re
        match = re.search(r"(\d+)\s*min", prompt_lower)
        minutos_str = f" de aprox. {match.group(1)} min" if match else ""

        if "tráfico" in prompt_lower or "congestión" in prompt_lower:
            texto = f"Estimado pasajero: retraso{minutos_str} debido a congestión vehicular en la vía."
        elif "choque" in prompt_lower or "accidente" in prompt_lower:
            texto = f"Estimado pasajero: retraso{minutos_str} por atención de incidente vial reportado."
        elif "desvío" in prompt_lower or "obra" in prompt_lower:
            texto = f"Estimado pasajero: retraso{minutos_str} por desvío temporal de ruta debido a obras."
        else:
            texto = f"Estimado pasajero: retraso estimado{minutos_str} por contingencia operativa en ruta."

        return RespuestaIA(texto=texto, modelo="mock-llm-v1", tokens_utilizados=20)


# ==============================================================================
# Patrón Decorator: Caché de respuestas del LLM
# ==============================================================================

class CacheIADecorator(IProveedorLLM):
    """DECORATOR: Evita costos de API y latencia cacheando prompts repetidos."""

    def __init__(self, proveedor_interno: IProveedorLLM):
        self._proveedor_interno = proveedor_interno
        self._cache: Dict[str, RespuestaIA] = {}
        self.llamadas_reales: int = 0

    def generar_explicacion(self, prompt: str) -> RespuestaIA:
        if prompt not in self._cache:
            self.llamadas_reales += 1
            self._cache[prompt] = self._proveedor_interno.generar_explicacion(prompt)
        return self._cache[prompt]

    def limpiar_cache(self) -> None:
        self._cache.clear()


# ==============================================================================
# Patrón Chain of Responsibility: Cadena de Guardrails de Seguridad
# ==============================================================================

@dataclass
class ContextoExplicacion:
    """Datos contextuales del dominio para contrastar la salida generada por el LLM."""
    motivo_telemetria: str
    minutos_retraso: int
    respuesta_ia: str


class IGuardrail(ABC):
    """Manejador base de la Cadena de Responsabilidad (Chain of Responsibility)."""

    def __init__(self):
        self.siguiente: Optional["IGuardrail"] = None

    def enlazar(self, siguiente: "IGuardrail") -> "IGuardrail":
        """Enlaza el siguiente guardrail en la cadena y lo retorna para facilitar encadenamiento."""
        self.siguiente = siguiente
        return siguiente

    @abstractmethod
    def validar(self, contexto: ContextoExplicacion) -> None:
        """Verifica una regla específica sobre la respuesta generada."""
        raise NotImplementedError

    def procesar(self, contexto: ContextoExplicacion) -> None:
        """Aplica su validación y delega al siguiente eslabón si existe."""
        self.validar(contexto)
        if self.siguiente is not None:
            self.siguiente.procesar(contexto)


class GuardrailConsistenciaTelemetria(IGuardrail):
    """Guardrail 1: Comprueba que la IA no alucine causas que contradigan la telemetría real."""

    def validar(self, contexto: ContextoExplicacion) -> None:
        resp_lower = contexto.respuesta_ia.lower()
        motivo_lower = contexto.motivo_telemetria.lower()

        # Si la telemetría indica congestión o tráfico, la IA no puede inventar fallas mecánicas graves
        if "tráfico" in motivo_lower or "congestión" in motivo_lower:
            alucinaciones_prohibidas = ["motor", "explosión", "incendio", "paro cardíaco", "cancelado"]
            for palabra in alucinaciones_prohibidas:
                if palabra in resp_lower:
                    raise ViolacionGuardrailError(
                        f"Guardrail de Consistencia: La IA alucinó '{palabra}', contradiciendo la telemetría de tráfico."
                    )

        # Si hay retraso positivo, la IA no puede afirmar que el bus no tiene retraso o que ya llegó
        if contexto.minutos_retraso > 0:
            if "no tiene retraso" in resp_lower or "ya llegó a su destino" in resp_lower:
                raise ViolacionGuardrailError(
                    "Guardrail de Consistencia: La IA afirma falsamente que el bus no registra demora."
                )


class GuardrailLongitudYTono(IGuardrail):
    """Guardrail 2: Garantiza brevedad (máx 250 caracteres) y tono respetuoso/institucional."""

    def validar(self, contexto: ContextoExplicacion) -> None:
        # Longitud máxima para tarjetas móviles de la PWA
        if len(contexto.respuesta_ia) > 250:
            raise ViolacionGuardrailError(
                f"Guardrail de Longitud: La respuesta excede los 250 caracteres ({len(contexto.respuesta_ia)})."
            )

        # Tono respetuoso: bloqueo de expresiones alarmistas o vulgares
        terminos_alarmistas = ["desastre", "pánico", "peligro mortal", "catástrofe"]
        for termino in terminos_alarmistas:
            if termino in contexto.respuesta_ia.lower():
                raise ViolacionGuardrailError(
                    f"Guardrail de Tono: Se detectó lenguaje alarmista ('{termino}') no institucional."
                )


# ==============================================================================
# Servicio Orquestador del componente de IA
# ==============================================================================

class ServicioExplicacionIA:
    """Orquesta la generación de explicaciones protegidas por caché y guardrails."""

    def __init__(
        self,
        proveedor: Optional[IProveedorLLM] = None,
        guardrail_chain: Optional[IGuardrail] = None,
        usar_cache: bool = True
    ):
        base_llm = proveedor or MockLLMAdapter()
        self.proveedor = CacheIADecorator(base_llm) if usar_cache else base_llm

        if guardrail_chain is None:
            # Construye la cadena por defecto: Consistencia -> Longitud y Tono
            cadena = GuardrailConsistenciaTelemetria()
            cadena.enlazar(GuardrailLongitudYTono())
            self.guardrail_chain = cadena
        else:
            self.guardrail_chain = guardrail_chain

    def explicar_retraso(self, motivo_telemetria: str, minutos_retraso: int) -> str:
        """Genera una explicación validada o retorna itinerario normal si no hay retraso."""
        if minutos_retraso <= 0:
            return "El bus se encuentra operando dentro del itinerario normal."

        prompt = f"Explicar retraso de {minutos_retraso} min por motivo: {motivo_telemetria}"
        respuesta: RespuestaIA = self.proveedor.generar_explicacion(prompt)

        # Valida a través de la cadena de guardrails
        contexto = ContextoExplicacion(
            motivo_telemetria=motivo_telemetria,
            minutos_retraso=minutos_retraso,
            respuesta_ia=respuesta.texto
        )
        self.guardrail_chain.procesar(contexto)

        return respuesta.texto
