#!/usr/bin/env python3
"""
Fix MDX compilation errors by wrapping inline code with < or > in backticks
"""
import re
import sys
from pathlib import Path

def fix_inline_code(content):
    """Wrap patterns with < or > in backticks if not already in code blocks"""
    lines = content.split('\n')
    result = []
    in_code_block = False

    for line in lines:
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # Skip if in code block
        if in_code_block:
            result.append(line)
            continue

        # Fix patterns outside backticks
        # Pattern: <number or >=number or <=number followed by text
        line = re.sub(r'(?<!`)((?:<|>|>=|<=)\d+[a-zA-Z/\-+]*(?:\s|,|\)|$))', r'`\1`', line)

        # Fix Result<T>, Task<T>, etc. - generic types
        line = re.sub(r'(?<!`)(\b\w+<[A-Z]>)(?!`)', r'`\1`', line)

        # Fix Task<ValidationResult> etc.
        line = re.sub(r'(?<!`)(\bTask<\w+>)(?!`)', r'`\1`', line)

        # Fix generic method calls like GetAsync<T>
        line = re.sub(r'(?<!`)(\w+<[A-Z]>\()', r'`\1`', line)

        # Clean up double backticks
        line = line.replace('``', '`')

        result.append(line)

    return '\n'.join(result)

def process_file(file_path):
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content = fix_inline_code(content)

        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✓ Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    # Files with errors from the build output
    error_files = [
        "docs/decisiones-de-arquitectura/adr-002-aws-ecs-fargate-contenedores.md",
        "docs/decisiones-de-arquitectura/adr-003-keycloak-sso-autenticacion.md",
        "docs/decisiones-de-arquitectura/adr-004-aws-secrets-manager.md",
        "docs/decisiones-de-arquitectura/adr-005-aws-parameter-store-configs.md",
        "docs/decisiones-de-arquitectura/adr-006-postgresql-base-datos.md",
        "docs/decisiones-de-arquitectura/adr-007-s3-almacenamiento-objetos.md",
        "docs/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md",
        "docs/decisiones-de-arquitectura/adr-009-debezium-cdc.md",
        "docs/decisiones-de-arquitectura/adr-010-kong-api-gateway.md",
        "docs/decisiones-de-arquitectura/adr-011-terraform-iac.md",
        "docs/decisiones-de-arquitectura/adr-012-github-actions-cicd.md",
        "docs/decisiones-de-arquitectura/adr-013-github-container-registry.md",
        "docs/decisiones-de-arquitectura/adr-014-grafana-stack-observabilidad.md",
        "docs/fundamentos-corporativos/estandares/arquitectura/clean-architecture.md",
        "docs/fundamentos-corporativos/estandares/arquitectura/cqrs-event-driven.md",
        "docs/fundamentos-corporativos/estandares/seguridad/identity-access-management.md",
        "docs/guias-arquitectura/transactional-outbox.md",
    ]

    base_path = Path("/mnt/d/dev/work/talma/tlm-doc-architecture")
    fixed_count = 0

    for file_rel in error_files:
        file_path = base_path / file_rel
        if file_path.exists():
            if process_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠ File not found: {file_path}")

    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
