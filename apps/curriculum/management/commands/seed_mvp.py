"""
Comando de inicializacion automatica de datos semilla para el MVP de CodeQuest.
Carga estudiantes de prueba, temas del Agreement, conceptos teoricos (CU-03),
reto de clasificacion (CU-01), reto de preguntas (CU-02) e insignias.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Estudiante
from apps.accounts.services import AuthService
from apps.challenges.models import ClasificacionItem, Opcion, Pregunta, Reto
from apps.curriculum.models import Tema, Teoria
from apps.gamification.models import Insignia


class Command(BaseCommand):
    help = "Puebla la base de datos con el contenido inicial del Sprint 1 de CodeQuest."

    @transaction.atomic
    def handle(self, *args, **options):
        if Tema.objects.exists():
            self.stdout.write(self.style.SUCCESS("Los datos del MVP ya estan cargados."))
            return

        self.stdout.write("Sembrando datos iniciales del MVP CodeQuest...")

        # 1. Cuentas de Estudiantes (CU-04)
        password_hash = AuthService.crear_hash_contrasena("CodeQuest2026!")
        usuarios_iniciales = [
            ("estudiante@uaz.edu.mx", "Estudiante Demo UAZ"),
            ("oliver@uaz.edu.mx", "Oliver Germain Saldivar Elizalde"),
            ("antonio@uaz.edu.mx", "Ángel Antonio de la Cruz Díaz"),
            ("saul@uaz.edu.mx", "Saúl Isaac Jaime Partida"),
            ("fernando@uaz.edu.mx", "Fernando Tiscareño Herrera"),
        ]
        for correo, nombre in usuarios_iniciales:
            Estudiante.objects.get_or_create(
                correo=correo,
                defaults={"nombre": nombre, "contrasena_hash": password_hash},
            )

        # 2. Insignias
        Insignia.objects.get_or_create(
            codigo="ARQUITECTO_REQ",
            defaults={
                "nombre": "Arquitecto de Requerimientos",
                "descripcion": "Clasificó correctamente todos los requerimientos funcionales y no funcionales al evaluar el proyecto.",
                "icono": "🏛️",
            },
        )
        Insignia.objects.get_or_create(
            codigo="MENTE_ANALITICA",
            defaults={
                "nombre": "Mente Analítica",
                "descripcion": "Superó el reto de evaluación teórica revisando la retroalimentación formativa.",
                "icono": "🧠",
            },
        )

        # 3. Temas del Agreement y SRS (CU-03)
        tema_req = Tema.objects.create(
            nombre="Conceptos básicos de requerimientos",
            descripcion="Ingeniería de requerimientos, elicitación, especificación SRS y clasificación en funcionales y no funcionales.",
            icono="📋",
            orden=1,
        )
        tema_bd = Tema.objects.create(
            nombre="Bases de datos y Diagramas ER",
            descripcion="Modelado relacional, integridad referencial, transacciones ACID, índices y diseño Entidad-Relación.",
            icono="🗄️",
            orden=2,
        )
        tema_alg = Tema.objects.create(
            nombre="Algoritmos, Estructuras y Diagramas de Flujo",
            descripcion="Complejidad algorítmica, estructuras lineales/no lineales y representación lógica mediante diagramas.",
            icono="🔀",
            orden=3,
        )
        tema_web = Tema.objects.create(
            nombre="Desarrollo Web y Ciberseguridad",
            descripcion="Arquitectura cliente-servidor, APIs REST, hashing unidireccional de contraseñas y protección de sesiones.",
            icono="🛡️",
            orden=4,
        )

        # 4. Conceptos Teoricos por Tema (CU-03)
        Teoria.objects.bulk_create(
            [
                Teoria(
                    id_tema=tema_req,
                    titulo_concepto="1. Requerimientos Funcionales (RF)",
                    contenido=(
                        "Definen QUÉ debe hacer el sistema: los comportamientos, servicios o "
                        "funciones específicas que el software ejecutará ante determinadas entradas "
                        "(Wiegers & Beatty, 2013). Ejemplo: 'El encargado debe poder descargar el "
                        "registro de fallas en formato PDF'."
                    ),
                ),
                Teoria(
                    id_tema=tema_req,
                    titulo_concepto="2. Requerimientos No Funcionales (RNF / Atributos de Calidad)",
                    contenido=(
                        "Especifican CÓMO debe comportarse el sistema: restricciones de rendimiento, "
                        "seguridad, usabilidad, portabilidad y disponibilidad. Ejemplo: 'El sistema "
                        "debe completar la autenticación en menos de 2 segundos' o 'Las contraseñas "
                        "deben almacenarse con encriptación unidireccional'."
                    ),
                ),
                Teoria(
                    id_tema=tema_req,
                    titulo_concepto="3. Trazabilidad en ISO/IEC 29110",
                    contenido=(
                        "Consiste en vincular cada requisito del cliente con su Caso de Uso (CU), "
                        "el componente de arquitectura que lo implementa (SDS) y el caso de prueba "
                        "que lo verifica, garantizando que ningún requisito quede huérfano."
                    ),
                ),
                Teoria(
                    id_tema=tema_bd,
                    titulo_concepto="1. Propiedades ACID e Índices en PostgreSQL",
                    contenido=(
                        "Una transacción garantiza Atomicidad, Consistencia, Aislamiento y Durabilidad. "
                        "El uso de índices B-Tree y compuestos evita escaneos secuenciales (Seq Scan) "
                        "en consultas frecuentes como la validación de sesiones o el historial de puntos."
                    ),
                ),
                Teoria(
                    id_tema=tema_alg,
                    titulo_concepto="1. Estructuras de Datos y Retornos Tempranos",
                    contenido=(
                        "Seleccionar la estructura adecuada (tablas hash O(1) vs listas O(n)) optimiza "
                        "el tiempo de respuesta. En la codificación, aplicar Early Returns reduce la "
                        "complejidad ciclomática y evita el anidamiento profundo."
                    ),
                ),
                Teoria(
                    id_tema=tema_web,
                    titulo_concepto="1. Hashing Unidireccional y Tokens JWT",
                    contenido=(
                        "Las contraseñas jamás se almacenan en texto plano; se procesan con algoritmos "
                        "como PBKDF2 o Argon2. La sesión se controla mediante JSON Web Tokens (JWT) "
                        "firmados criptográficamente."
                    ),
                ),
            ]
        )

        # 5. Reto CU-01: Clasificar Requerimientos
        reto_cu01 = Reto.objects.create(
            id_tema=tema_req,
            tipo="CLASIFICACION",
            titulo="CU-01: Clasificación de Requerimientos del Sistema Municipal",
            descripcion=(
                "Arrastra cada descripción del proyecto ficticio hacia el contenedor "
                "'Funcionales' o 'No Funcionales' según corresponda y evalúa tu clasificación."
            ),
            puntos_maximos=100,
            orden=1,
        )

        ClasificacionItem.objects.bulk_create(
            [
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="El Encargado de alumbrado público debe poder descargar el registro de fallas en PDF.",
                    categoria_correcta="FUNCIONAL",
                    orden=1,
                ),
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="El sistema debe cargar y responder en menos de 2 segundos.",
                    categoria_correcta="NO_FUNCIONAL",
                    orden=2,
                ),
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="El ciudadano debe poder registrar un reporte de bache adjuntando su ubicación.",
                    categoria_correcta="FUNCIONAL",
                    orden=3,
                ),
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="Las contraseñas de los usuarios deben almacenarse mediante un algoritmo hash unidireccional.",
                    categoria_correcta="NO_FUNCIONAL",
                    orden=4,
                ),
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="El sistema debe enviar un correo de confirmación cuando cambie el estatus de un reporte.",
                    categoria_correcta="FUNCIONAL",
                    orden=5,
                ),
                ClasificacionItem(
                    id_reto=reto_cu01,
                    descripcion="La interfaz web debe mantener su legibilidad sin superposición en resoluciones mínimas de 1280x720 píxeles.",
                    categoria_correcta="NO_FUNCIONAL",
                    orden=6,
                ),
            ]
        )

        # 6. Reto CU-02: Responder Pregunta con Retroalimentacion Teorica
        reto_cu02 = Reto.objects.create(
            id_tema=tema_req,
            tipo="PREGUNTA",
            titulo="CU-02: Evaluación de Ingeniería de Software y Arquitectura",
            descripcion=(
                "Responde cada reactivo antes de que expire el temporizador. Al enviar tu "
                "respuesta se desplegará la retroalimentación teórica obligatoria."
            ),
            puntos_maximos=150,
            orden=2,
        )

        p1 = Pregunta.objects.create(
            id_reto=reto_cu02,
            enunciado="¿Cuál de las siguientes afirmaciones describe correctamente un Requerimiento No Funcional (RNF)?",
            explicacion_teorica=(
                "Los Requerimientos No Funcionales definen atributos de calidad o restricciones "
                "operativas del sistema (como tiempos de respuesta sub-segundo, uso de hashing "
                "para seguridad o compatibilidad de resolución), mientras que los Funcionales "
                "describen acciones o servicios para el usuario."
            ),
            tiempo_limite_seg=30,
            orden=1,
        )
        Opcion.objects.bulk_create(
            [
                Opcion(
                    id_pregunta=p1,
                    texto="El sistema debe permitir al estudiante clasificar descripciones arrastrándolas.",
                    es_correcta=False,
                    orden=1,
                ),
                Opcion(
                    id_pregunta=p1,
                    texto="El modal de retroalimentación debe renderizarse en pantalla en menos de 1 segundo tras evaluar.",
                    es_correcta=True,
                    orden=2,
                ),
                Opcion(
                    id_pregunta=p1,
                    texto="El usuario puede consultar el catálogo de temas desde el menú principal.",
                    es_correcta=False,
                    orden=3,
                ),
            ]
        )

        p2 = Pregunta.objects.create(
            id_reto=reto_cu02,
            enunciado="Según el patrón arquitectónico Service Layer adoptado en el SDS, ¿cuál es la responsabilidad estricta de las Vistas (Views)?",
            explicacion_teorica=(
                "En una arquitectura con Service Layer (ADR-02), las vistas nunca contienen lógica "
                "de negocio ni cálculos directos sobre múltiples modelos. Su único rol es orquestar: "
                "validar la entrada HTTP, invocar al servicio correspondiente y retornar la respuesta."
            ),
            tiempo_limite_seg=30,
            orden=2,
        )
        Opcion.objects.bulk_create(
            [
                Opcion(
                    id_pregunta=p2,
                    texto="Ejecutar consultas SQL crudas y calcular penalizaciones de puntos directamente.",
                    es_correcta=False,
                    orden=1,
                ),
                Opcion(
                    id_pregunta=p2,
                    texto="Únicamente orquestar: validar la entrada, invocar al servicio y devolver la respuesta.",
                    es_correcta=True,
                    orden=2,
                ),
                Opcion(
                    id_pregunta=p2,
                    texto="Reemplazar por completo al ORM de Django mediante triggers en el navegador.",
                    es_correcta=False,
                    orden=3,
                ),
            ]
        )

        p3 = Pregunta.objects.create(
            id_reto=reto_cu02,
            enunciado="¿Por qué razón se crea un índice compuesto sobre (id_estudiante, fecha_evaluacion DESC) en la tabla registro_puntos?",
            explicacion_teorica=(
                "Sin el índice compuesto, PostgreSQL tendría que filtrar primero por id_estudiante "
                "y después realizar un ordenamiento (Sort) en memoria. Con el índice compuesto, los "
                "registros ya se encuentran pre-ordenados cronológicamente para cada estudiante."
            ),
            tiempo_limite_seg=30,
            orden=3,
        )
        Opcion.objects.bulk_create(
            [
                Opcion(
                    id_pregunta=p3,
                    texto="Para evitar un escaneo y ordenamiento en memoria al consultar el historial reciente del estudiante.",
                    es_correcta=True,
                    orden=1,
                ),
                Opcion(
                    id_pregunta=p3,
                    texto="Para permitir almacenar contraseñas en texto plano con mayor velocidad.",
                    es_correcta=False,
                    orden=2,
                ),
                Opcion(
                    id_pregunta=p3,
                    texto="Porque PostgreSQL prohíbe llaves foráneas si no llevan un índice DESC.",
                    es_correcta=False,
                    orden=3,
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS("MVP de CodeQuest sembrado con exito."))
