# Cuestionario — Laboratorio 04 (Grupo 06, RutaSIT Arequipa)

## 1. ¿Por qué se afirma que una decisión arquitectónica es aquella "costosa de cambiar"? Dé un ejemplo de su caso.
Porque condiciona muchas otras decisiones que se toman encima de ella. Cambiarla después no es tocar un archivo: obliga a rehacer código, datos, despliegue y a veces la forma de trabajar del equipo. Por eso se toma pronto y con cuidado.

En RutaSIT un ejemplo es usar WebSocket para enviar las posiciones a los pasajeros (ADR-003). Si a mitad del proyecto quisiéramos volver a polling, habría que reescribir el cliente PWA, el módulo de Notificaciones y la configuración de Nginx, y recalcular la capacidad del VPS, porque 1500 pasajeros consultando cada 5 s son unas 300 req/s más. En cambio, el color de los íconos del mapa no es una decisión arquitectónica: se cambia en minutos y no afecta a nada más.

## 2. ¿Cuál es la diferencia entre un requisito funcional y un atributo de calidad? ¿Por qué los atributos de calidad influyen más en la arquitectura?
Un requisito funcional dice **qué** hace el sistema; un atributo de calidad dice **qué tan bien** lo hace. En nuestro caso, "mostrar el ETA del próximo bus a un paradero" (RF-03) es funcional; "que esa información llegue en 15 s o menos con 300 buses y 1500 pasajeros" (QA-01) es un atributo de calidad.

Los atributos de calidad pesan más porque casi cualquier arquitectura puede cumplir un requisito funcional: el ETA se puede calcular en un monolito en capas, en microservicios o en un monolito modular. Lo que separa a esas opciones es si cumplen la latencia, la disponibilidad o el costo. En RutaSIT, el rendimiento en tiempo real fue lo que descartó el polling y nos llevó al modelo asíncrono con Redis.

## 3. Reescriba el requisito "el sistema debe ser seguro" como un escenario de atributo de calidad de seis partes.

| Parte | Valor |
| :--- | :--- |
| **Fuente** | Atacante externo con la contraseña filtrada de un operador del SIT. |
| **Estímulo** | Intenta iniciar sesión en el panel de supervisión desde una IP desconocida y modificar el trazado de una ruta. |
| **Entorno** | Operación normal, en horario laboral. |
| **Artefacto** | Módulo de autenticación del panel de operadores y endpoints administrativos del Catálogo SIT. |
| **Respuesta** | El sistema exige un segundo factor, bloquea la cuenta tras 5 intentos fallidos, registra el evento en el log de auditoría y avisa al administrador. |
| **Medida** | 100 % de los intentos sin segundo factor rechazados; alerta al administrador en 1 minuto o menos; 0 rutas modificadas sin autenticación completa; el log conserva IP, usuario y hora del 100 % de los intentos. |

## 4. Compare el monolito modular y los microservicios en términos de costo, modificabilidad y complejidad operativa. ¿En qué momento convendría migrar de uno a otro?

| Aspecto | Monolito modular | Microservicios |
| :--- | :--- | :--- |
| **Costo** | Un solo despliegue y una sola base; cabe en un VPS barato (R-03). | Un proceso por servicio, broker, varias bases y más memoria; normalmente varios servidores u orquestador. |
| **Modificabilidad** | Buena mientras se respeten los límites entre módulos; el riesgo es que se erosionen y todo termine acoplado. | Muy buena: cada servicio cambia y se despliega solo. A cambio, modificar un contrato entre servicios es costoso. |
| **Complejidad operativa** | Baja: un log, un despliegue, depuración local sencilla. | Alta: red entre servicios, trazas distribuidas, reintentos, consistencia eventual y CI/CD por servicio. |

Conviene migrar cuando un módulo concreto tenga necesidades que el monolito ya no puede atender: por ejemplo, si RutaSIT se extiende a otras ciudades y la ingesta GPS necesita escalar de forma independiente, o si equipos distintos necesitan desplegar a ritmos distintos. Lo sensato es extraer primero ese módulo (en nuestro caso Ingesta o Notificaciones), aprovechando que ya tiene una frontera definida, y no migrar todo de una vez.

## 5. ¿Qué ventajas ofrece Diagram as Code frente a herramientas de dibujo como PowerPoint? Mencione al menos tres.
1. **Se versiona en Git junto al código.** Cada cambio del diagrama queda en el historial y se ve como diferencia línea por línea.
2. **Se revisa en un Pull Request**, igual que el código: un compañero puede comentar una flecha o un módulo concreto.
3. **Se regenera automáticamente.** Una GitHub Action con mermaid-cli puede producir la imagen en cada push, así que imagen y fuente no se desincronizan.
4. **Es texto**, así que la IA lo genera y corrige con facilidad. En esta práctica hicimos así los tres diagramas y luego los revisamos línea por línea.

## 6. ¿Qué elementos debe contener un ADR y por qué es importante registrar también las alternativas descartadas?
Un ADR debe tener: título, estado (Propuesto, Aceptado, Rechazado o Reemplazado), fecha, decisores, contexto (los drivers que motivan la decisión, citados por su ID), las alternativas consideradas, la decisión escrita en voz activa y las consecuencias positivas y negativas.

Registrar las alternativas descartadas evita repetir la misma discusión. Si dentro de seis meses alguien propone "pasemos a microservicios", el ADR-001 muestra que se evaluó, por qué obtuvo 2.35 frente a 4.45 y bajo qué restricciones (R-01, R-03). Si esas restricciones cambian, por ejemplo con más presupuesto o más personas, queda claro que la decisión se puede revisar y desde dónde partir.

## 7. Describa un caso de esta práctica en el que la IA haya generado una propuesta incorrecta o sesgada. ¿Cómo lo detectaron?
Hubo dos casos.

El primero fue un sesgo hacia lo que está de moda: al pedirle un stack, la IA mencionó microservicios con brokers distribuidos para un equipo de 2 personas con 1 mes de plazo. Lo detectamos contrastándolo con R-01, R-02 y R-03.

El segundo fue más sutil. En la crítica a la Alternativa A, la IA afirmó que un Django síncrono "agota los workers con 30 req/s" y que 2,5 millones de inserciones diarias saturan el disco "al 100 % de I/O". Sonaba convincente, pero al aplicar la Ley de Little ($L = \lambda \times W = 30 \times 0.05 = 1.5$ peticiones en curso) vimos que unos pocos workers atienden esa carga, y que 2,5 millones al día son solo 30 inserciones por segundo. Corregimos el puntaje de A de 3.35 a 3.60 y anotamos el cálculo en la matriz y en la bitácora. La conclusión no cambió, pero ahora se apoya en el motivo real: A no tiene empuje en tiempo real hacia los pasajeros.

## 8. ¿Qué riesgos éticos y de confidencialidad existen al usar asistentes de IA para diseñar la arquitectura de un sistema real?
- **Fuga de información.** Lo que se pega en un prompt puede quedar almacenado por el proveedor. En un sistema real como el SIT, eso incluye trazados internos, direcciones IP de servidores, credenciales o datos de operadores protegidos por la Ley N.° 29733. Por eso en la bitácora reemplazamos los nombres de los integrantes.
- **Alucinaciones presentadas con seguridad.** La IA da cifras y capacidades que suenan técnicas pero no están medidas, como nos pasó con la carga de Django. Si nadie las verifica, terminan justificando decisiones caras.
- **Sesgos.** Tiende a recomendar las tecnologías más populares en internet (microservicios, Kubernetes) aunque no encajen con el presupuesto ni con el equipo.
- **Responsabilidad difusa.** Si una decisión sugerida por la IA falla en producción, la responsabilidad sigue siendo del equipo. No se puede firmar un ADR que no entendemos.
- **Honestidad académica y licencias.** Hay que declarar qué produjo la IA y revisar que el código o los textos generados no copien material con licencia restrictiva.
