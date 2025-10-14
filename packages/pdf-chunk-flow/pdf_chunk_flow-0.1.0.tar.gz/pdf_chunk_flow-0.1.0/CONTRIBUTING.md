# Contribuyendo a PDF Chunk Flow

¡Gracias por tu interés en contribuir a PDF Chunk Flow! 🎉

## 🚀 Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un [issue](https://github.com/facuvegaingenieer/pdf_chunk_flow/issues) con:

- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento esperado vs actual
- Versión de Python y del paquete
- Logs relevantes

### Sugerir Features

Para sugerir nuevas funcionalidades:

1. Abre un [issue](https://github.com/facuvegaingenieer/pdf_chunk_flow/issues)
2. Describe el feature y su caso de uso
3. Explica por qué sería útil para otros usuarios

### Pull Requests

1. **Fork el repositorio**
   ```bash
   git clone https://github.com/facuvegaingenieer/pdf_chunk_flow.git
   cd pdf_chunk_flow
   ```

2. **Crea una rama**
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```

3. **Configura el entorno de desarrollo**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **Haz tus cambios**
   - Escribe código limpio y bien documentado
   - Agrega tests para tu funcionalidad
   - Actualiza la documentación si es necesario

5. **Ejecuta los tests**
   ```bash
   pytest tests/ -v
   pytest tests/ --cov
   ```

6. **Commit tus cambios**
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   ```

7. **Push y crea un Pull Request**
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```

## 📝 Guía de Estilo

### Código Python

- Seguir [PEP 8](https://pep8.org/)
- Docstrings en formato Google
- Type hints cuando sea posible
- Nombres descriptivos de variables y funciones

### Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `docs:` - Cambios en documentación
- `test:` - Agregar o modificar tests
- `refactor:` - Refactorización sin cambiar funcionalidad
- `style:` - Cambios de formato (espacios, etc)
- `chore:` - Tareas de mantenimiento

### Tests

- Todos los nuevos features deben tener tests
- Mantener cobertura >90%
- Tests deben ser independientes y reproducibles
- Usar fixtures de pytest cuando sea apropiado

## 🧪 Ejecutar Tests Localmente

```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov --cov-report=html

# Tests específicos
pytest tests/test_extract.py -v
pytest tests/test_transform.py::TestPdfTransformer::test_create_chunks -v

# Tests con logs
pytest tests/ -v -s
```

## 📚 Documentación

- Actualizar README.md si agregas funcionalidades
- Agregar docstrings a funciones y clases
- Incluir ejemplos de uso cuando sea relevante

## ✅ Checklist del Pull Request

Antes de enviar tu PR, verifica:

- [ ] Los tests pasan localmente
- [ ] Agregaste tests para tu código nuevo
- [ ] La documentación está actualizada
- [ ] El código sigue el estilo del proyecto
- [ ] Los commits siguen Conventional Commits
- [ ] El PR tiene una descripción clara

## 🤝 Código de Conducta

- Sé respetuoso y constructivo
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a otros contribuyentes

## 💡 ¿Necesitas Ayuda?

- Abre un [issue](https://github.com/facuvegaingenieer/pdf_chunk_flow/issues)
- Contacta al mantenedor: facundo.vega1234@gmail.com

¡Gracias por contribuir! 🚀

