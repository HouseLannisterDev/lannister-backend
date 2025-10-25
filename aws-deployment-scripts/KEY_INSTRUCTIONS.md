# INSTRUCCIONES PARA CLAVES SSH DE AWS EC2
# ==========================================

## Este archivo reemplaza la clave privada .pem que NO debe estar en el repositorio

## Cómo obtener tu clave privada:

1. **Si ya tienes la clave (.pem):**
   - Guárdala en este directorio como `lannister-backend-key.pem`
   - Asegúrate de que tenga permisos correctos: `chmod 400 lannister-backend-key.pem`
   - NO la agregues al repositorio (ya está en .gitignore)

2. **Si necesitas crear una nueva clave:**
   - Ve a AWS Console > EC2 > Key Pairs
   - Crea un nuevo par de claves llamado "lannister-backend-key"
   - Descarga el archivo .pem y guárdalo en este directorio
   - Configura permisos: `chmod 400 lannister-backend-key.pem`

3. **Para conectarte a EC2:**
   ```bash
   ssh -i lannister-backend-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```

## IMPORTANTE:
- NUNCA compartas la clave .pem
- NUNCA la subas a Git, GitHub, o cualquier repositorio público
- Si la clave se compromete, créala nuevamente desde AWS Console
- Mantén una copia segura en un lugar privado (1Password, AWS Secrets Manager, etc.)

## Ubicación segura de la clave:
- Local: `aws-deployment-scripts/lannister-backend-key.pem` (ignorada por Git)
- Backup: AWS Secrets Manager o gestor de contraseñas
