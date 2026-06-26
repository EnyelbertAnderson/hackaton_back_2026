## 1. Endpoint de Evaluación Individual

Procesa una fotografía del examen manuscrito de un estudiante enviada desde el celular del docente. El procesamiento se realiza estrictamente en memoria (sin persistencia en disco) para resguardar la privacidad y seguridad de los datos de menores de edad.

* **URL:** `/evaluar`
* **Método:** `POST`
* **Content-Type:** `multipart/form-data`

### Parámetros de Entrada (Form Fields)

| Campo | Tipo | Requerido | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- | :--- |
| `alumno_id` | `string` | Sí | Identificador único del estudiante. | `ALU-2026-041` |
| `nombre_alumno` | `string` | Sí | Nombre completo del estudiante. | `Juan Pérez Flores` |
| `file` | `file (binary)` | Sí | Fotografía o captura del examen (PNG, JPG, JPEG). | `examen_matematica.png` |

### JSON de Respuesta (`200 OK`)

El pipeline retorna un objeto JSON estructurado mapeado directamente desde el `context_packet.py` compartido:


```

```text
SUCCESS

```json
{
  "alumno_id": "ALU-2026-041",
  "nombre_alumno": "Juan Pérez Flores",
  "nota": "Aceptable (A)",
  "criterio_citado": "Competencia: Resuelve problemas de forma, movimiento y localización. Capacidad: Modela objetos con formas geométricas.",
  "feedback": "Buen planteamiento conceptual y ejecución del cálculo numérico del área. Sin embargo, omitió colocar las unidades correspondientes en la respuesta final (cm²).",
  "transcripcion_ocr": "[Transcripción de Examen] El alumno resolvió: Area = 5cm x 4cm = 20."
}

```

---

## 2. Endpoint de Diagnóstico de Aula

Consolida la analítica predictiva y formativa extraída por el agente de diagnóstico (`diagnostic` corriendo bajo el free-tier de Gemini) para pintar los gráficos, listas de errores y recomendaciones curriculares en el Dashboard del docente.

* **URL:** `/aula/{aula_id}/diagnostico`
* **Método:** `GET`
* **Parámetro de Ruta:** `aula_id` (string) — Identificador de la sección escolar.

### JSON de Respuesta (`200 OK`)

```json
{
  "aula_id": "5to-A-Primaria",
  "errores_comunes": [
    "Confusión recurrente entre los conceptos curriculares de perímetro y área.",
    "Omisión sistemática de unidades de medida (cm, m, cm²) en las respuestas finales."
  ],
  "puntos_fuertes": [
    "Excelente nivel de planteamiento algebraico y manipulación de variables en el aula.",
    "Comprensión unánime de operaciones aritméticas básicas de multiplicación."
  ],
  "recomendaciones_cneb": [
    "Reforzar de manera práctica la competencia 'Resuelve problemas de forma, movimiento y localización' del Currículo Nacional.",
    "Implementar dinámicas de modelado gráfico y geométrico antes de pasar al cálculo aritmético puro."
  ],
  "resumen_rendimiento": "El 65% del aula domina la formulación teórica pero requiere refuerzo inmediato en geometría y unidades aplicadas."
}

```

---

## 3. Guía de Integración desde el Frontend (Next.js / TypeScript)

Para conectar tu formulario de captura y componentes del Dashboard, consume la API usando los siguientes contratos de tipos:

### Definición de Interfaces (TypeScript)

```typescript
// frontend/lib/types/api.ts

export interface EvaluacionResponse {
  alumno_id: string;
  nombre_alumno: string;
  nota: string;
  criterio_citado: string;
  feedback: string;
  transcripcion_ocr?: string;
}

export interface DiagnosticoAulaResponse {
  aula_id: string;
  errores_comunes: string[];
  puntos_fuertes: string[];
  recomendaciones_cneb: string[];
  resumen_rendimiento: string;
}

```

### Ejemplo de Petición con Fetch (`FormData`)

```typescript
// Ejemplo de llamada para subir el examen desde el celular del docente
async function enviarExamen(alumnoId: string, nombre: string, archivoImagen: File): Promise<EvaluacionResponse> {
  const formData = new FormData();
  formData.append('alumno_id', alumnoId);
  formData.append('nombre_alumno', nombre);
  formData.append('file', archivoImagen);

  const response = await fetch('[http://127.0.0.1:8000/evaluar](http://127.0.0.1:8000/evaluar)', {
    method: 'POST',
    body: formData, // Fetch asigna automáticamente el Content-Type correcto como multipart/form-data
  });

  if (!response.ok) {
    throw new Error('Error al procesar la evaluación agéntica');
  }

  return response.json();
}

```

---

## 4. Códigos de Estado Comunes

* **`200 OK`**: Petición procesada exitosamente por el pipeline agéntico.
* **`400 Bad Request`**: El archivo adjunto no corresponde a una extensión de imagen válida (`image/*`).
* **`500 Internal Server Error`**: Excepción no controlada dentro de la secuencia de agentes o falla de 
```


# Configuración del Entorno de Ñawi
GOOGLE_API_KEY=tu_api_key_real_de_google_ai_studio
ANTHROPIC_API_KEY=tu_api_key_real_de_anthropic_console
OPENAI_API_KEY=tu_api_key_real_de_openai_si_usas_el_fallback

# Configuración de Rutas de Datos
CHROMA_DATA_DIR=./chroma_data