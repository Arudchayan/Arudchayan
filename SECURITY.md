# Security Policy

## Supported versions

Security fixes are applied to the latest 1.0.x release. Older versions are not supported.

| Version | Supported |
| --- | --- |
| 1.0.x | Yes |
| < 1.0 | No |

## Reporting a vulnerability

Please do not open a public issue for a security problem. Report it privately through GitHub Security Advisories:

<https://github.com/Arudchayan/Arudchayan/security/advisories/new>

Include as much of the following as possible:

- The affected version or commit.
- Python version and operating system.
- A minimal reproduction, including the seed when simulation behavior is involved.
- The impact and any conditions required to trigger the issue.
- A suggested fix, if you have one.

Maintainers will acknowledge the report, assess its impact, and coordinate a fix and disclosure timeline with the reporter. Please allow reasonable time for a fix before public disclosure.

## Scope

In scope:

- The battle engine, deterministic RNG, evaluation, training, and CLI.
- Loading of policy and Q-table files distributed with or consumed by the project.
- Packaging, installation, and GitHub Actions configuration.
- Denial-of-service conditions caused by untrusted benchmark inputs.

Out of scope:

- Vulnerabilities in optional dependencies such as PyTorch or NumPy; report those upstream.
- Incorrect or unsupported Pokémon data, names, or sprites.
- Results produced by third-party agents, policies, or experiment code.
- Issues that require modifying the local installation or running with elevated privileges.

PokéLab is an independent research project and is not affiliated with Nintendo, Game Freak, or The Pokémon Company.
