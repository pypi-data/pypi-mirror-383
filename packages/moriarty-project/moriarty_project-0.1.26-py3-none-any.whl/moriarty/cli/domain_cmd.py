"""Comandos de scanning de domínios/IPs."""

import asyncio
import json
from typing import Optional, Dict, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box

from moriarty.modules.web_crawler import WebCrawler
from moriarty.modules.port_scanner import PortScanner, PROFILES
from moriarty.modules.passive_recon import PassiveRecon

app = typer.Typer(help="🔍 Ferramentas avançadas de reconhecimento de domínios")
console = Console()


@app.command("scan")
def scan_full(
    target: str = typer.Argument(..., help="Domain ou IP alvo"),
    modules: str = typer.Option(
        "all",
        "--modules",
        "-m",
        help="Módulos: all,dns,subdiscover,wayback,ports,ssl,crawl,fuzzer,template-scan,vuln-scan,waf-detect",
    ),
    stealth: int = typer.Option(0, "--stealth", "-s", help="Stealth level (0-4)"),
    threads: int = typer.Option(10, "--threads", "-t", help="Threads concorrentes"),
    timeout: int = typer.Option(30, "--timeout", help="Timeout em segundos"),
    output: str = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
    verbose: bool = typer.Option(False, "--verbose", help="Ativar saída detalhada"),
):
    """
    🔍 Scan completo de domínio/IP com 14 módulos.
    
    Exemplos:
        moriarty domain scan example.com
        moriarty domain scan 8.8.8.8 --stealth 3
        moriarty domain scan target.com --modules dns,ports,ssl
    """
    from moriarty.modules.domain_scanner import DomainScanner
    import asyncio
    import logging
    
    # Suprime logs verbosos globalmente
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("moriarty").setLevel(logging.ERROR)
    
    scanner = DomainScanner(
        target=target,
        modules=modules.split(",") if modules != "all" else None,
        stealth_level=stealth,
        threads=threads,
        timeout=timeout,
        verbose=verbose,
    )
    
    asyncio.run(scanner.run())
    
    if output:
        scanner.export(output)
        console.print(f"[green]✅[/green] Results saved to: [red]{output}[/red]\n")


@app.command("subdiscover")
def subdomain_discovery(
    domain: str = typer.Argument(..., help="Domínio alvo"),
    sources: str = typer.Option("all", "--sources", "-s", help="Fontes: all,crtsh,virustotal,..."),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validar subdomínios encontrados"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Busca recursiva"),
    wordlist: str = typer.Option(None, "--wordlist", "-w", help="Wordlist personalizada"),
    output: str = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
):
    """
    🔍 Descoberta de subdomínios usando 20+ fontes.
    
    Fontes suportadas:
    - crt.sh (Certificate Transparency)
    - VirusTotal
    - SecurityTrails
    - Shodan
    - DNSDumpster
    - AlienVault OTX
    - ThreatCrowd
    - Wayback Machine
    - CommonCrawl
    - Google Dorking
    - Bing
    - Yahoo
    - Ask
    - DNS Bruteforce
    - Zone Transfer
    - Reverse DNS
    - DNSSEC
    - NSEC Walking
    - Subdomain Permutations
    - GitHub Code Search
    """
    from moriarty.modules.subdomain_discovery import SubdomainDiscovery
    import asyncio
    
    console.print(f"[bold red]🔍 Descobrindo subdomínios de:[/bold red] {domain}\n")
    
    discovery = SubdomainDiscovery(
        domain=domain,
        sources=sources.split(",") if sources != "all" else None,
        validate=validate,
        recursive=recursive,
        wordlist=wordlist,
    )
    
    results = asyncio.run(discovery.discover())
    
    console.print(f"\n[green]✅ {len(results)} subdomínios encontrados[/green]")
    
    for subdomain in sorted(results):
        console.print(f"  • {subdomain}")
    
    if output:
        discovery.export(results, output)


@app.command("wayback")
def wayback_urls(
    domain: str = typer.Argument(..., help="Domínio alvo"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validar URLs ativas"),
    filter_ext: str = typer.Option(None, "--filter", "-f", help="Filtrar extensões (ex: php,asp,jsp)"),
    status_filter: str = typer.Option(None, "--status", help="Filtrar status codes (ex: 200,404,301)"),
    years: int = typer.Option(5, "--years", "-y", help="Anos para buscar"),
    output: str = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
):
    """
    🕰️ Descobre URLs históricas via Wayback Machine.
    
    Exemplos:
        moriarty domain wayback example.com
        moriarty domain wayback target.com --filter php,asp --years 10
    """
    from moriarty.modules.wayback_discovery import WaybackDiscovery
    import asyncio
    
    console.print(f"[bold red]🕰️ Buscando URLs históricas de:[/bold red] {domain}\n")
    
    wayback = WaybackDiscovery(
        domain=domain,
        validate=validate,
        filter_extensions=filter_ext.split(",") if filter_ext else None,
        filter_status_codes=[int(code.strip()) for code in status_filter.split(",") if code.strip()]
        if status_filter
        else None,
        years_back=years,
    )
    
    urls = asyncio.run(wayback.discover())
    
    console.print(f"\n[green]✅ {len(urls)} URLs encontradas[/green]")
    
    if output:
        wayback.export(urls, output)


@app.command("template-scan")
def template_scan(
    target: str = typer.Argument(..., help="Alvo (domain ou IP)"),
    templates: str = typer.Option(None, "--templates", "-t", help="Path para templates ou tag"),
    severity: str = typer.Option("all", "--severity", "-s", help="Severidade: all,critical,high,medium,low"),
    threads: int = typer.Option(20, "--threads", help="Threads concorrentes"),
    output: str = typer.Option(None, "--output", "-o", help="Arquivo de saída"),
):
    """
    📝 Scan baseado em templates (estilo Nuclei).
    
    Exemplos:
        moriarty domain template-scan example.com
        moriarty domain template-scan target.com --templates cves/
        moriarty domain template-scan target.com --severity critical,high
    """
    import asyncio

    from moriarty.modules.template_scanner import TemplateScanner

    console.print(f"[bold red]📝 Template scan em:[/bold red] {target}\n")

    scanner = TemplateScanner(
        target=target,
        templates_path=templates,
        severity_filter=severity.split(",") if severity != "all" else None,
        threads=threads,
    )

    results = asyncio.run(scanner.scan())

    console.print(f"\n[bold]Resultados:[/bold]")
    for severity_level in ["critical", "high", "medium", "low", "info"]:
        findings = [r for r in results if r.severity == severity_level]
        if findings:
            color = {"critical": "red", "high": "yellow", "medium": "blue", "low": "green", "info": "dim"}[severity_level]
            console.print(f"[{color}]• {severity_level.upper()}: {len(findings)} findings[/{color}]")

    if output:
        scanner.export(results, output)


@app.command("pipeline")
def run_pipeline(
    pipeline_file: str = typer.Argument(..., help="Arquivo YAML do pipeline"),
    target: str = typer.Option(None, "--target", "-t", help="Alvo (sobrescreve YAML)"),
    vars_file: str = typer.Option(None, "--vars", "-v", help="Arquivo de variáveis"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simular sem executar"),
):
    """
    🔄 Executa pipeline de scan via YAML declarativo.
    
    Exemplo de pipeline.yaml:
        name: "Full Recon"
        target: "example.com"
        stages:
          - name: "DNS Discovery"
            module: "dns"
          - name: "Subdomain Enum"
            module: "subdiscover"
          - name: "Port Scan"
            module: "ports"
    """
    from moriarty.modules.pipeline_orchestrator import PipelineOrchestrator
    import asyncio
    
    console.print(f"[bold red]🔄 Executando pipeline:[/bold red] {pipeline_file}\n")
    
    orchestrator = PipelineOrchestrator(
        pipeline_file=pipeline_file,
        target_override=target,
        vars_file=vars_file,
        dry_run=dry_run,
    )
    
    asyncio.run(orchestrator.run())


@app.command("stealth")
def stealth_command(
    action: str = typer.Argument(..., help="Ação: scan, config, proxy, test"),
    target: str = typer.Option(None, "--target", "-t", help="Alvo para scan/test"),
    level: int = typer.Option(2, "--level", "-l", help="Nível stealth (0-4)"),
):
    """
    🥷 Stealth Mode - Sistema completo de evasão.
    
    Níveis:
        0 - Disabled: Sem stealth
        1 - Low: Randomização básica
        2 - Medium: Proxies + timing
        3 - High: Fragmentação + adaptativo
        4 - Paranoid: Todas técnicas + decoys
    
    Exemplos:
        moriarty domain stealth scan example.com --level 3
        moriarty domain stealth config
        moriarty domain stealth test --target example.com
    """
    from moriarty.modules.stealth_mode import StealthMode
    import asyncio
    
    stealth = StealthMode(level=level)
    
    if action == "config":
        stealth.show_config()
    elif action == "scan":
        if not target:
            console.print("[red]❌ --target é obrigatório para scan[/red]")
            raise typer.Exit(1)
        asyncio.run(stealth.scan(target))
    elif action == "proxy":
        stealth.manage_proxies()
    elif action == "test":
        if not target:
            console.print("[red]❌ --target é obrigatório para test[/red]")
            raise typer.Exit(1)
        asyncio.run(stealth.test_capabilities(target))
    else:
        console.print(f"[red]❌ Ação inválida: {action}[/red]")


# A função port_scan foi movida para a implementação mais completa abaixo


@app.command("waf-detect")
def waf_detection(
    target: str = typer.Argument(..., help="URL alvo"),
    bypass: bool = typer.Option(False, "--bypass", "-b", help="Tentar bypass automático"),
):
    """
    🛡️ Detecta WAF/IPS e tenta bypass automático.
    
    Detecta:
    - Cloudflare
    - AWS WAF
    - Akamai
    - Imperva
    - F5 BIG-IP
    - ModSecurity
    - Sucuri
    - Barracuda
    - Fortinet
    """
    from moriarty.modules.waf_detector import WAFDetector
    import asyncio
    
    console.print(f"[bold red]🛡️ Detectando WAF em:[/bold red] {target}\n")
    
    detector = WAFDetector(target=target)
    waf_info = asyncio.run(detector.detect())
    
    if waf_info:
        console.print(f"[yellow]⚠️ WAF detectado:[/yellow] {waf_info['name']}")
        console.print(f"[dim]Confidence: {waf_info['confidence']}%[/dim]")
        
        if bypass:
            console.print("\n[red]🔓 Tentando bypass...[/red]")
            bypass_methods = asyncio.run(detector.attempt_bypass())
            
            for method in bypass_methods:
                if method['success']:
                    console.print(f"[green]✅ Bypass bem-sucedido:[/green] {method['technique']}")
    else:
        console.print("[green]✅ Nenhum WAF detectado[/green]")


__all__ = ["app"]
@app.command("recon")
def passive_recon(
    domain: str = typer.Argument(..., help="Domínio alvo"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Arquivo JSON de saída"),
    status_only: bool = typer.Option(False, "--status-only", help="Mostrar apenas resumo"),
):
    """
    🌐 Coleta passiva de inteligência sobre domínios.
    
    Exemplos:
        moriarty domain recon example.com
        moriarty domain recon target.com --output resultado.json
    """
    import asyncio
    import json
    import logging
    from datetime import datetime
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    
    # Configuração de logs
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("moriarty").setLevel(logging.ERROR)
    
    console = Console()
    
    # Cabeçalho
    console.print(f"\n[bold red]🌐 Moriarty Passive Recon[/bold red]")
    console.print(f"[dim]Alvo:[/dim] {domain}")
    console.print(f"[dim]Data:[/dim] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    async def _run():
        with console.status(f"[bold green]Coletando informações sobre [red]{domain}[/red]..."):
            recon = PassiveRecon(domain)
            try:
                return await recon.collect()
            finally:
                await recon.close()

    try:
        result = asyncio.run(_run())
        payload = result.to_dict()
        
        if status_only:
            sub_count = sum(len(v) for v in payload["subdomains"].values())
            console.print(f"[bold]🔍 Resumo do Reconhecimento[/bold]")
            console.print(f"  • [red]Subdomínios:[/red] {sub_count} encontrados")
            console.print(f"  • [red]Fontes:[/red] {', '.join(payload['subdomains'].keys()) or 'nenhuma'}")
            console.print(f"  • [red]Credenciais vazadas:[/red] {len(payload['leaks'])}")
            return
            
        # Seção de Subdomínios
        if payload.get("subdomains"):
            table = Table(title="[bold]🌐 Subdomínios Encontrados[/bold]", box=box.ROUNDED)
            table.add_column("Subdomínio", style="red")
            table.add_column("Fonte", style="green")
            
            for source, subdomains in payload["subdomains"].items():
                for sub in subdomains:
                    table.add_row(sub, source)
            
            console.print(Panel.fit(table, border_style="blue"))
        
        # Seção de Tecnologias
        if payload.get("technologies", {}).get("detections"):
            tech_table = Table(title="[bold]🛠️ Tecnologias Detectadas[/bold]", box=box.ROUNDED)
            tech_table.add_column("Tecnologia", style="red")
            tech_table.add_column("Confiança", style="green")
            tech_table.add_column("Categoria", style="magenta")
            
            for tech in payload["technologies"]["detections"]:
                tech_table.add_row(
                    tech["name"],
                    f"{tech['confidence']}%",
                    ", ".join(tech.get("categories", []))
                )
            
            console.print(Panel.fit(tech_table, border_style="blue"))
        
        # Seção de Segurança
        security_table = Table(title="[bold]🔒 Análise de Segurança[/bold]", box=box.ROUNDED)
        security_table.add_column("Item", style="red")
        security_table.add_column("Status", style="green")
        
        # Verifica HSTS
        headers = payload.get("technologies", {}).get("headers", {})
        hsts = "Sim" if "strict-transport-security" in str(headers).lower() else "Não"
        security_table.add_row("HSTS Habilitado", hsts)
        
        # Verifica XSS Protection
        xss_protection = "Sim" if "x-xss-protection" in str(headers).lower() else "Não"
        security_table.add_row("Proteção XSS", xss_protection)
        
        # Verifica Content Security Policy
        csp = "Sim" if "content-security-policy" in str(headers).lower() else "Não"
        security_table.add_row("Content Security Policy", csp)
        
        console.print(Panel.fit(security_table, border_style="blue"))
        
        # Seção de Reputação
        if payload.get("reputation"):
            rep_table = Table(title="[bold]📊 Reputação do Domínio[/bold]", box=box.ROUNDED)
            rep_table.add_column("Fonte", style="red")
            rep_table.add_column("Status", style="green")
            
            for source, data in payload["reputation"].items():
                if isinstance(data, dict) and data.get("pulses") is not None:
                    rep_table.add_row(source, f"{len(data['pulses'])} ameaças conhecidas")
                elif source == "alienvault" and data.get("pulses") is not None:
                    rep_table.add_row("AlienVault OTX", f"{len(data['pulses'])} ameaças conhecidas")
            
            console.print(Panel.fit(rep_table, border_style="blue"))
        
        # Seção de Informações WHOIS
        if payload.get("whois"):
            whois_info = "\n".join(line for line in payload["whois"].split("\n") 
                                 if not line.startswith("%") and line.strip())
            console.print(Panel.fit(
                f"[bold]📝 Informações de Registro (WHOIS)[/bold]\n\n[dim]{whois_info}",
                border_style="blue"
            ))
        
        if output:
            with open(output, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
            console.print(f"\n[green]✓[/green] Resultados salvos em: [red]{output}[/red]")
    
    except Exception as e:
        console.print(f"[red]✗ Erro durante o reconhecimento:[/red] {str(e)}")
        if output:
            with open(output, "w", encoding="utf-8") as handle:
                json.dump({"error": str(e)}, handle, indent=2)
            console.print(f"[yellow]⚠  Log de erro salvo em: {output}[/yellow]")


import asyncio

async def _port_scan_async(
    target: str,
    profile: str,
    stealth: int,
    resolve_services: bool,
    check_vulns: bool,
    format: str,
    output: Optional[str]
):
    """Função assíncrona que realiza a varredura de portas."""
    # Código da função port_scan aqui...
    console = Console()
    
    # Valida os parâmetros
    def validate_parameters():
        if stealth < 0 or stealth > 5:
            console.print("[red]Erro:[/red] O nível de stealth deve estar entre 0 e 5")
            raise typer.Exit(1)
            
        if profile not in PROFILES:
            console.print(f"[red]Erro:[/red] Perfil inválido. Use um dos seguintes: {', '.join(PROFILES.keys())}")
            raise typer.Exit(1)
    
    # Configura o console do Rich
    console = Console()
    
    # Valida os parâmetros
    validate_parameters()
    
    # Usa o perfil especificado ou o padrão 'quick'
    ports = PROFILES.get(profile.lower(), PROFILES["quick"])
    
    # Configura o arquivo de saída
    output_path = Path(output) if output else None
    if output_path:
        if output_path.suffix not in (".json", ".txt", ".md"):
            console.print("[yellow]Aviso:[/yellow] Extensão de arquivo não suportada. Usando .json")
            output_path = output_path.with_suffix(".json")
    
    # Configura a barra de progresso
    progress_columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ]
    
    # Cabeçalho da varredura
    console.rule(f"🔍 [bold red]Varredura de Portas[/bold red]")
    
    # Tabela de informações
    info_table = Table.grid(padding=(0, 1))
    info_table.add_row("🌐 Alvo:", f"[bold]{target}")
    info_table.add_row("🔢 Portas:", f"[red]{ports}")
    info_table.add_row("🛡️  Nível de stealth:", f"[yellow]{stealth}")
    info_table.add_row("🔍 Detecção de serviços:", "[green]Ativada[/green]" if resolve_services else "[red]Desativada[/red]")
    info_table.add_row("⚠️  Verificação de vulnerabilidades:", "[green]Ativada[/green]" if check_vulns else "[red]Desativada[/red]")
    
    console.print(Panel(info_table, title="[bold]Configuração da Varredura[/bold]", border_style="red"))
    console.print()
    
    async def run_scan() -> List[PortScanResult]:
        """Executa a varredura de portas."""
        # Usa sempre TCP Connect que não requer privilégios de root
        console.print("[yellow]Aviso:[/yellow] Usando varredura TCP Connect (não requer privilégios de root).")
        scan_type = "tcp"
        
        # Cria o scanner Nmap
        scanner = PortScanner(
            target=target,
            ports=ports,
            scan_type=scan_type,
            stealth_level=stealth,
            resolve_services=resolve_services,
            check_vulns=check_vulns,
        )
        
        # Executa o scan e retorna os resultados
        return await scanner.scan()

    console.print("🚀 Iniciando varredura de portas...\n")
    
    # Executa a varredura com barra de progresso
    with Progress(*progress_columns) as progress:
        task = progress.add_task("[red]Escaneando portas...", total=100)
        
        try:
            # Executa o scan de forma assíncrona
            results = await run_scan()
            progress.update(task, completed=100)
            
            if not results:
                console.print("\n[yellow]⚠️  Nenhuma porta aberta detectada[/yellow]")
                return
                
            output_format = format.lower()
            
            if output_format == "json":
                output_text = json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
                if not output_path:
                    console.print_json(data=json.loads(output_text))
            elif output_format == "markdown":
                # Formata a saída em Markdown
                output_lines = [
                    f"# Resultados da varredura de portas em {target}\n",
                    "| Porta | Protocolo | Status | Serviço | Versão | Vulnerabilidades |",
                    "|-------|-----------|--------|---------|---------|------------------|"
                ]
                
                for result in results:
                    service = getattr(result, 'service', None)
                    status = "🟢 ABERTA" if getattr(result, 'status', '') == "open" else "🔴 FECHADA"
                    service_name = getattr(service, 'name', 'desconhecido') if service else "desconhecido"
                    version = getattr(service, 'version', '') if service else ""
                    vulns = ", ".join(service.vulns) if service and hasattr(service, 'vulns') and service.vulns else "-"
                    
                    output_lines.append(
                        f"| {getattr(result, 'port', '')} | "
                        f"{getattr(result, 'protocol', 'tcp').upper()} | "
                        f"{status} | "
                        f"{service_name} | "
                        f"{version} | "
                        f"{vulns if vulns and vulns != '[]' else '-'} |"
                    )
                
                # Adiciona resumo
                open_ports = [r for r in results if getattr(r, 'status', '') == "open"]
                output_text = "\n".join(output_lines)
                output_text += f"\n\n✅ **Varredura concluída!** {len(open_ports)} porta(s) aberta(s) encontrada(s)."
                
                if not output_path:
                    console.print(output_text)
            else:  # Formato de texto simples
                # Cria tabela de resultados
                table = Table(
                    title=f"🔍 Resultados da varredura em {target}",
                    box=box.ROUNDED,
                    header_style="bold magenta",
                    expand=True
                )
                
                # Adiciona colunas
                table.add_column("Porta", style="red", justify="right")
                table.add_column("Protocolo", style="magenta")
                table.add_column("Status", style="green")
                table.add_column("Serviço", style="yellow")
                table.add_column("Versão", style="blue")
                table.add_column("Vulnerabilidades", style="red")
                
                # Adiciona linhas com os resultados
                for result in results:
                    service = getattr(result, 'service', None)
                    status = "[green]ABERTA[/green]" if getattr(result, 'status', '') == "open" else "[red]FECHADA[/red]"
                    service_name = getattr(service, 'name', 'desconhecido') if service else "desconhecido"
                    version = getattr(service, 'version', '') if service else ""
                    vulns = ", ".join(service.vulns) if service and hasattr(service, 'vulns') and service.vulns else "-"
                    
                    table.add_row(
                        str(getattr(result, 'port', '')),
                        getattr(result, 'protocol', 'tcp').upper(),
                        status,
                        service_name,
                        version,
                        vulns if vulns and vulns != "[]" else "-"
                    )
                
                # Exibe a tabela
                console.print(table)
                
                # Resumo
                open_ports = [r for r in results if getattr(r, 'status', '') == "open"]
                console.print(f"\n✅ [bold green]Varredura concluída![/bold green] {len(open_ports)} porta(s) aberta(s) encontrada(s).")
                
                # Prepara o texto para salvar em arquivo
                output_text = str(table)
        
            # Salva em arquivo se especificado
            if output_path:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(output_text)
                    console.print(f"\n💾 [bold]Resultados salvos em:[/bold] [red]{output_path.absolute()}[/red]")
                except Exception as e:
                    console.print(f"\n❌ [bold red]Erro ao salvar arquivo:[/bold red] {str(e)}")
    
        except KeyboardInterrupt:
            console.print("\n❌ [bold red]Varredura cancelada pelo usuário[/bold red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n❌ [bold red]Erro durante a varredura:[/bold red] {str(e)}")
            if "Errno 8" in str(e) or "Name or service not known" in str(e):
                console.print("💡 [yellow]Dica:[/yellow] Não foi possível resolver o nome do host. Verifique a conexão com a internet ou o nome do domínio.")
            if "No module named 'nmap'" in str(e):
                console.print("💡 [yellow]Dica:[/yellow] O módulo 'python-nmap' não está instalado. Instale com: [red]pip install python-nmap[/red]")
            raise typer.Exit(1)

async def run_port_scan(
    target: str,
    profile: str,
    stealth: int,
    concurrency: int,
    timeout: float,
    output: Optional[str],
    format: str,
):
    """Função assíncrona que executa a varredura de portas."""
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from pathlib import Path
    import json
    
    # Valida os parâmetros
    if stealth < 0 or stealth > 5:
        console.print("[red]Erro:[/red] O nível de stealth deve estar entre 0 e 5")
        raise typer.Exit(1)
        
    if profile not in PROFILES:
        console.print(f"[red]Erro:[/red] Perfil inválido. Use um dos seguintes: {', '.join(PROFILES.keys())}")
        raise typer.Exit(1)
    
    # Usa o perfil especificado ou o padrão 'quick'
    ports = PROFILES.get(profile.lower(), PROFILES["quick"])
    
    # Configura o arquivo de saída
    output_path = Path(output) if output else None
    if output_path:
        if output_path.suffix not in (".json", ".txt", ".md"):
            console.print("[yellow]Aviso:[/yellow] Extensão de arquivo não suportada. Usando .json")
            output_path = output_path.with_suffix(".json")
    
    # Configura a barra de progresso
    progress_columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ]
    
    # Cabeçalho da varredura
    console.rule(f"🔍 [bold red]Varredura de Portas[/bold red]")
    
    # Tabela de informações
    info_table = Table.grid(padding=(0, 1))
    info_table.add_row("🌐 Alvo:", f"[bold]{target}")
    info_table.add_row("🔢 Portas:", f"[red]{ports}")
    info_table.add_row("🛡️  Nível de stealth:", f"[yellow]{stealth}")
    info_table.add_row("🔍 Detecção de serviços:", "[green]Ativada[/green]")
    info_table.add_row("⚠️  Verificação de vulnerabilidades:", "[green]Ativada[/green]")
    
    console.print(Panel(info_table, title="[bold]Configuração da Varredura[/bold]", border_style="red"))
    console.print()
    
    # Executa a varredura com barra de progresso
    with Progress(*progress_columns) as progress:
        task = progress.add_task("[red]Escaneando portas...", total=100)
        
        try:
            # Cria o scanner Nmap
            scanner = PortScanner(
                target=target,
                ports=ports,
                scan_type="syn" if stealth < 2 else "tcp",
                stealth_level=stealth,
                resolve_services=True,
                check_vulns=True,
            )
            
            # Executa o scan de forma assíncrona
            results = await scanner.scan()
            progress.update(task, completed=100)
            
            if not results:
                console.print("\n[yellow]⚠️  Nenhuma porta aberta detectada[/yellow]")
                return
            
            # Formata a saída
            output_format = format.lower()
            
            if output_format == "json":
                output_text = json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
                if not output_path:
                    console.print_json(data=json.loads(output_text))
            elif output_format == "markdown":
                output_lines = [
                    f"# Resultados da varredura de portas em {target}\n",
                    "| Porta | Protocolo | Status | Serviço | Versão |",
                    "|-------|-----------|--------|---------|---------|"
                ]
                
                for result in results:
                    service = getattr(result, 'service', None)
                    status = "🟢 ABERTA" if getattr(result, 'status', '') == "open" else "🔴 FECHADA"
                    service_name = getattr(service, 'name', 'desconhecido') if service else "desconhecido"
                    version = getattr(service, 'version', '') if service else ""
                    
                    output_lines.append(
                        f"| {getattr(result, 'port', '')} | "
                        f"{getattr(result, 'protocol', 'tcp').upper()} | "
                        f"{status} | "
                        f"{service_name} | "
                        f"{version} |"
                    )
                
                # Adiciona resumo
                open_ports = [r for r in results if getattr(r, 'status', '') == "open"]
                output_text = "\n".join(output_lines)
                output_text += f"\n\n✅ **Varredura concluída!** {len(open_ports)} porta(s) aberta(s) encontrada(s)."
                
                if not output_path:
                    console.print(output_text)
            else:  # Formato de texto simples
                # Cria tabela de resultados
                table = Table(
                    title=f"🔍 Resultados da varredura em {target}",
                    box=box.ROUNDED,
                    header_style="bold magenta",
                    expand=True
                )
                
                # Adiciona colunas
                table.add_column("Porta", style="red", justify="right")
                table.add_column("Protocolo", style="magenta")
                table.add_column("Status", style="green")
                table.add_column("Serviço", style="yellow")
                table.add_column("Versão", style="blue")
                
                # Adiciona linhas com os resultados
                for result in results:
                    service = getattr(result, 'service', None)
                    status = "[green]ABERTA[/green]" if getattr(result, 'status', '') == "open" else "[red]FECHADA[/red]"
                    service_name = getattr(service, 'name', 'desconhecido') if service else "desconhecido"
                    version = getattr(service, 'version', '') if service else ""
                    
                    table.add_row(
                        str(getattr(result, 'port', '')),
                        getattr(result, 'protocol', 'tcp').upper(),
                        status,
                        service_name,
                        version,
                    )
                
                # Exibe a tabela
                console.print(table)
                
                # Resumo
                open_ports = [r for r in results if getattr(r, 'status', '') == "open"]
                console.print(f"\n✅ [bold green]Varredura concluída![/bold green] {len(open_ports)} porta(s) aberta(s) encontrada(s).")
                
                # Prepara o texto para salvar em arquivo
                output_text = str(table)
    
            # Salva em arquivo se especificado
            if output_path:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(output_text)
                    console.print(f"\n💾 [bold]Resultados salvos em:[/bold] [red]{output_path.absolute()}[/red]")
                except Exception as e:
                    console.print(f"\n❌ [bold red]Erro ao salvar arquivo:[/bold red] {str(e)}")
    
        except KeyboardInterrupt:
            console.print("\n❌ [bold red]Varredura cancelada pelo usuário[/bold red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n❌ [bold red]Erro durante a varredura:[/bold red] {str(e)}")
            if "Errno 8" in str(e) or "Name or service not known" in str(e):
                console.print("💡 [yellow]Dica:[/yellow] Não foi possível resolver o nome do host. Verifique a conexão com a internet ou o nome do domínio.")
            if "No module named 'nmap'" in str(e):
                console.print("💡 [yellow]Dica:[/yellow] O módulo 'python-nmap' não está instalado. Instale com: [red]pip install python-nmap[/red]")
            raise typer.Exit(1)

@app.command("ports")
def port_scan(
    target: str = typer.Argument(..., help="Domínio ou IP para escanear"),
    profile: str = typer.Option(
        "quick", 
        "--profile", 
        "-p", 
        help=f"Perfil de varredura: {', '.join(PROFILES.keys())}"
    ),
    stealth: int = typer.Option(
        0,
        "--stealth",
        "-s",
        min=0,
        max=5,
        help="Nível de stealth (0-5, maior = mais lento e discreto)",
    ),
    concurrency: int = typer.Option(
        200, 
        "--concurrency", 
        "-c", 
        help="Número de conexões simultâneas",
        min=1,
        max=1000,
    ),
    timeout: float = typer.Option(
        2.0, 
        "--timeout", 
        "-t", 
        help="Timeout por porta em segundos",
        min=0.5,
        max=30.0,
    ),
    output: Optional[str] = typer.Option(
        None, 
        "--output", 
        "-o", 
        help="Arquivo de saída (formato: .json, .txt, .md)"
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Formato de saída: text, json, markdown",
    ),
    resolve_services: bool = typer.Option(
        True,
        "--resolve/--no-resolve",
        help="Tentar identificar serviços nas portas abertas",
    ),
    check_vulns: bool = typer.Option(
        True,
        "--vulns/--no-vulns",
        help="Verificar vulnerabilidades conhecidas",
    ),
):
    """
    🔍 Varredura avançada de portas com detecção de serviços e vulnerabilidades usando Nmap.
    
    Exemplos:
        moriarty domain ports example.com
        moriarty domain ports 192.168.1.1 --profile full --stealth 3
        moriarty domain ports target.com -o resultado.json --format json
    """
    import asyncio
    import json
    import os
    import sys
    from pathlib import Path
    from typing import List, Dict, Any, Optional
    
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TaskProgressColumn,
    )
    from rich.panel import Panel
    from rich.table import Table, box
    from rich.console import Console
    
    from moriarty.modules.port_scanner_nmap import PortScanner, PortScanResult, ServiceInfo
    
    # Mapeia os perfis para o formato do Nmap
    port_profiles = {
        "quick": "21-23,25,53,80,110,111,135,139,143,389,443,445,465,587,993,995,1433,1521,2049,3306,3389,5432,5900,6379,8080,8443,9000,10000,27017",
        "web": "80,443,8080,8443,8000,8888,10443,4443",
        "mail": "25,110,143,465,587,993,995",
        "db": "1433,1521,27017-27019,28017,3306,5000,5432,5984,6379,8081",
        "full": "1-1024",
        "all": "1-65535",
    }
    
    # Verifica se o Nmap está instalado
    def check_nmap_installed() -> bool:
        """Verifica se o Nmap está instalado no sistema."""
        try:
            import nmap
            return True
        except ImportError:
            return False
    
    # Valida os parâmetros de entrada
    def validate_parameters() -> None:
        """Valida os parâmetros de entrada."""
        if not check_nmap_installed():
            console.print("❌ [bold red]Erro:[/bold red] O módulo 'python-nmap' não está instalado.")
            console.print("💡 [yellow]Dica:[/yellow] Instale com: pip install python-nmap")
            raise typer.Exit(1)
            
        if stealth < 0 or stealth > 5:
            console.print("❌ [bold red]Erro:[/bold red] O nível de stealth deve estar entre 0 e 5.")
            raise typer.Exit(1)
    
    # Inicializa o console do Rich
    console = Console()
    
    # Valida os parâmetros
    validate_parameters()
    
    # Usa o perfil especificado ou o padrão 'quick'
    ports = port_profiles.get(profile.lower(), port_profiles["quick"])
    
    # Configura o arquivo de saída
    output_path = Path(output) if output else None
    if output_path:
        if output_path.suffix not in (".json", ".txt", ".md"):
            console.print("[yellow]Aviso:[/yellow] Extensão de arquivo não suportada. Usando .json")
            output_path = output_path.with_suffix(".json")
    
    # Configura a barra de progresso
    progress_columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ]
    
    # Cabeçalho da varredura
    console.rule(f"🔍 [bold red]Varredura de Portas[/bold red]")
    
    # Tabela de informações
    info_table = Table.grid(padding=(0, 1))
    info_table.add_row("🌐 Alvo:", f"[bold]{target}")
    info_table.add_row("🔢 Portas:", f"[red]{ports}")
    info_table.add_row("🛡️  Nível de stealth:", f"[yellow]{stealth}")
    info_table.add_row("🔍 Detecção de serviços:", "[green]Ativada[/green]" if resolve_services else "[red]Desativada[/red]")
    info_table.add_row("⚠️  Verificação de vulnerabilidades:", "[green]Ativada[/green]" if check_vulns else "[red]Desativada[/red]")
    
    console.print(Panel(info_table, title="[bold]Configuração da Varredura[/bold]", border_style="red"))
    console.print()
    
    async def run_scan() -> List[PortScanResult]:
        """Executa a varredura de portas."""
        # Usa sempre TCP Connect que não requer privilégios de root
        console.print("[yellow]Aviso:[/yellow] Usando varredura TCP Connect (não requer privilégios de root).")
        scan_type = "tcp"
        
        # Cria o scanner Nmap
        scanner = PortScanner(
            target=target,
            ports=ports,
            scan_type=scan_type,
            stealth_level=stealth,
            resolve_services=resolve_services,
            check_vulns=check_vulns,
        )
        
        # Executa o scan e retorna os resultados
        return await scanner.scan()

    console.print("🚀 Iniciando varredura de portas...\n")
    
    # Função para salvar resultados em diferentes formatos
    def save_results(results, output_path, format):
        output_format = format.lower()
        
        try:
            if output_format == "json":
                output_text = json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_text)
            elif output_format == "markdown":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("# Resultados da Varredura de Portas\n\n")
                    f.write("| Porta | Estado | Serviço | Versão |\n")
                    f.write("|-------|--------|---------|---------|\n")
                    for result in results:
                        if result.state == 'open':
                            service = result.service or "desconhecido"
                            version = result.version or ""
                            f.write(f"| {result.port} | ABERTA | {service} | {version} |\n")
            else:  # text
                with open(output_path, 'w', encoding='utf-8') as f:
                    for result in results:
                        if result.state == 'open':
                            service = result.service or "desconhecido"
                            version = f" ({result.version})" if result.version else ""
                            f.write(f"Porta {result.port}/tcp: ABERTA - {service}{version}\n")
        except Exception as e:
            console.print(f"❌ [bold red]Erro ao salvar o arquivo:[/bold red] {str(e)}")
            raise typer.Exit(1)
    
    # Executa o scan de forma assíncrona
    with Progress(*progress_columns) as progress:
        task = progress.add_task("[red]Escaneando portas...", total=100)
        
        try:
            # Executa a função assíncrona
            results = asyncio.run(run_scan())
            progress.update(task, completed=100)
            
            # Exibe os resultados
            if results:
                # Cria uma tabela para exibir os resultados
                table = Table(title="[bold]Resultados da Varredura[/bold]")
                table.add_column("Porta", style="red", no_wrap=True)
                table.add_column("Estado", style="green")
                table.add_column("Serviço", style="yellow")
                table.add_column("Versão", style="magenta")
                
                for result in results:
                    if result.state == 'open':
                        service = result.service or "desconhecido"
                        version = result.version or ""
                        table.add_row(
                            str(result.port),
                            "[green]ABERTA[/green]",
                            service,
                            version
                        )
                
                console.print()
                console.print(table)
                
                # Salva os resultados em um arquivo, se solicitado
                if output_path:
                    save_results(results, output_path, format)
                    console.print(f"\n✅ Resultados salvos em: [bold red]{output_path}[/bold red]")
                
                # Exibe saída JSON no console se não houver arquivo de saída e o formato for JSON
                if format.lower() == "json" and not output_path:
                    output_text = json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
                    console.print_json(data=json.loads(output_text))
                    
            else:
                console.print("\n❌ Nenhuma porta aberta encontrada ou ocorreu um erro durante a varredura.")
                
        except Exception as e:
            progress.update(task, completed=100)
            console.print(f"\n❌ [bold red]Erro durante a varredura:[/bold red] {str(e)}")
            if "Errno 8" in str(e) or "Name or service not known" in str(e):
                console.print("💡 [yellow]Dica:[/yellow] Não foi possível resolver o nome do host. Verifique a conexão com a internet ou o nome do domínio.")
            raise typer.Exit(1)


@app.command("crawl")
def crawl(
    domain: str = typer.Argument(..., help="Alvo base (ex: https://example.com)"),
    max_depth: int = typer.Option(2, "--max-depth", help="Profundidade máxima"),
    max_pages: int = typer.Option(100, "--max-pages", help="Número máximo de páginas a serem rastreadas"),
    concurrency: int = typer.Option(10, "--concurrency", help="Workers paralelos"),
    follow_subdomains: bool = typer.Option(False, "--follow-subdomains", help="Seguir subdomínios"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Arquivo JSON de saída"),
):
    """Crawler leve para mapear formulários e rotas.
    
    Exemplos:
        moriarty domain crawl https://example.com
        moriarty domain crawl https://example.com --max-depth 3 --max-pages 50
    """
    import asyncio
    import json
    from typing import Dict, Any
    from pathlib import Path

    async def _run():
        crawler = WebCrawler(
            base_url=domain,
            max_pages=max_pages,
            max_depth=max_depth,
            concurrency=concurrency,
            follow_subdomains=follow_subdomains,
        )
        try:
            return await crawler.crawl()
        finally:
            await crawler.close()

    try:
        console.print(f"🚀 Iniciando crawler em [red]{domain}[/red]...")
        pages = asyncio.run(_run())
        
        # Cria um dicionário seguro para serialização
        safe_pages = {}
        for url, page in pages.items():
            safe_pages[url] = {
                'url': url,
                'title': getattr(page, 'title', ''),
                'forms': [form.__dict__ for form in getattr(page, 'forms', [])],
                'links': getattr(page, 'links', []),
                'status_code': getattr(page, 'status_code', 0)
            }
        
        # Exibe resumo
        summary = {
            "total_pages": len(pages),
            "forms": sum(len(page.get('forms', [])) for page in safe_pages.values()),
            "links_unicos": len({link for page in safe_pages.values() for link in page.get('links', [])})
        }
        
        console.print("\n📊 [bold]Resumo do Crawling:[/bold]")
        console.print(f"• Páginas processadas: {summary['total_pages']}")
        console.print(f"• Formulários encontrados: {summary['forms']}")
        console.print(f"• Links únicos: {summary['links_unicos']}")

        # Salva em arquivo se especificado
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "summary": summary,
                    "pages": safe_pages
                }, f, indent=2, ensure_ascii=False)
            console.print(f"\n💾 [bold]Resultados salvos em:[/bold] [red]{output_path.absolute()}[/red]")
            
    except Exception as e:
        console.print(f"\n❌ [bold red]Erro durante o crawling:[/bold red] {str(e)}")
        if "Failed to establish a new connection" in str(e):
            console.print("💡 [yellow]Dica:[/yellow] Verifique sua conexão com a internet ou a URL fornecida.")
        raise typer.Exit(1)
