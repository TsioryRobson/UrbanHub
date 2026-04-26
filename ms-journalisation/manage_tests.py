#!/usr/bin/env python
"""
Script utilitaire pour gérer les tests du microservice Journalisation
"""

import subprocess
import sys
import argparse


def run_all_tests():
    """Exécute tous les tests"""
    print("🧪 Exécution de tous les tests...")
    result = subprocess.run(["pytest", "-v"], cwd=".")
    return result.returncode


def run_tests_with_coverage():
    """Exécute les tests avec rapport de couverture"""
    print("📊 Exécution des tests avec couverture...")
    result = subprocess.run([
        "pytest",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term",
        "-v"
    ], cwd=".")
    return result.returncode


def run_specific_test_file(filepath):
    """Exécute un fichier de test spécifique"""
    print(f"🧪 Exécution du fichier {filepath}...")
    result = subprocess.run(["pytest", filepath, "-v"], cwd=".")
    return result.returncode


def run_domain_tests():
    """Exécute les tests du domain"""
    print("🧪 Exécution des tests du domain...")
    result = subprocess.run(["pytest", "tests/unit/domain/", "-v"], cwd=".")
    return result.returncode


def run_application_tests():
    """Exécute les tests de l'application"""
    print("🧪 Exécution des tests de l'application...")
    result = subprocess.run(["pytest", "tests/unit/application/", "-v"], cwd=".")
    return result.returncode


def run_adapter_tests():
    """Exécute les tests des adapters"""
    print("🧪 Exécution des tests des adapters...")
    result = subprocess.run(["pytest", "tests/unit/adapters/", "-v"], cwd=".")
    return result.returncode


def run_main():
    """Exécute le microservice"""
    print("🚀 Démarrage du microservice...")
    result = subprocess.run(["python", "src/main.py"], cwd=".")
    return result.returncode


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Script de gestion du microservice Journalisation"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Exécuter tous les tests"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Exécuter les tests avec couverture"
    )

    parser.add_argument(
        "--domain",
        action="store_true",
        help="Exécuter les tests du domain"
    )

    parser.add_argument(
        "--application",
        action="store_true",
        help="Exécuter les tests de l'application"
    )

    parser.add_argument(
        "--adapters",
        action="store_true",
        help="Exécuter les tests des adapters"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Exécuter un fichier de test spécifique"
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Exécuter le microservice"
    )

    args = parser.parse_args()

    # Si aucune option n'est fournie, exécuter tous les tests
    if not any(vars(args).values()):
        returncode = run_all_tests()
    elif args.all:
        returncode = run_all_tests()
    elif args.coverage:
        returncode = run_tests_with_coverage()
    elif args.domain:
        returncode = run_domain_tests()
    elif args.application:
        returncode = run_application_tests()
    elif args.adapters:
        returncode = run_adapter_tests()
    elif args.file:
        returncode = run_specific_test_file(args.file)
    elif args.run:
        returncode = run_main()
    else:
        parser.print_help()
        return 1

    return returncode


if __name__ == "__main__":
    sys.exit(main())
