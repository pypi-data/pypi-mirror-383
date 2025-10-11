"""Port scanning avançado com detecção de serviços e vulnerabilidades."""
from __future__ import annotations

import asyncio
import json
import re
import ssl
import contextlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import dns.asyncresolver
import structlog
from rich.console import Console
from rich.progress import track
from rich.table import Table, box

logger = structlog.get_logger(__name__)
console = Console()

# Perfis de varredura
PROFILES = {
    "quick": [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 389, 443, 445, 
              465, 587, 993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 
              8080, 8443, 9000, 10000, 27017],
    "web": [80, 443, 8080, 8443, 8000, 8888, 10443, 4443],
    "mail": [25, 110, 143, 465, 587, 993, 995],
    "db": [1433, 1521, 27017, 27018, 27019, 28017, 3306, 5000, 5432, 5984, 6379, 8081],
    "full": list(range(1, 1025)),
    "all": list(range(1, 65536)),
}

# URL base para atualizações de serviços e vulnerabilidades
SERVICES_DB_URL = "https://raw.githubusercontent.com/nmap/nmap/master/nmap-services"
VULN_DB_URL = "https://cve.mitre.org/data/downloads/allitems.csv"

# Diretório para armazenar dados locais
DATA_DIR = Path.home() / ".moriarty" / "data"
SERVICES_DB = DATA_DIR / "services.yml"
VULN_DB = DATA_DIR / "vulnerabilities.yml"

# Garante que o diretório de dados existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Estrutura para armazenar assinaturas de serviços
@dataclass
class ServiceSignature:
    name: str
    port: int
    protocol: str = "tcp"
    banner_patterns: List[str] = field(default_factory=list)
    ssl_ports: Set[int] = field(default_factory=set)
    version_pattern: Optional[str] = None
    cpe: Optional[str] = None
    vulns: List[Dict[str, str]] = field(default_factory=list)
    last_updated: Optional[datetime] = None

# Dicionário para armazenar assinaturas de serviços
SERVICE_SIGNATURES: Dict[str, ServiceSignature] = {}

# Mapeamento de portas para serviços comuns
SERVICE_MAP = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPCbind",
    135: "MSRPC",
    139: "NetBIOS",
    143: "IMAP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    500: "IKE",
    515: "LPD",
    554: "RTSP",
    587: "SMTP (Submission)",
    631: "IPP",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1194: "OpenVPN",
    1433: "MSSQL",
    1521: "Oracle",
    2049: "NFS",
    2375: "Docker",
    2376: "Docker TLS",
    3000: "Node.js",
    3306: "MySQL",
    3389: "RDP",
    5000: "UPnP",
    5432: "PostgreSQL",
    5601: "Kibana",
    5672: "AMQP",
    5900: "VNC",
    5984: "CouchDB",
    6379: "Redis",
    8000: "HTTP-Alt",
    8008: "HTTP-Alt",
    8080: "HTTP-Proxy",
    8081: "HTTP-Alt",
    8088: "HTTP-Alt",
    8089: "Splunk",
    8090: "HTTP-Alt",
    8091: "Couchbase",
    8096: "Plex",
    8125: "StatsD",
    8140: "Puppet",
    8200: "Vault",
    8300: "Consul",
    8333: "Bitcoin",
    8443: "HTTPS-Alt",
    8500: "Consul",
    8545: "Ethereum",
    8765: "Grafana",
    8888: "Jupyter",
    9000: "SonarQube",
    9001: "Tor",
    9042: "Cassandra",
    9090: "Prometheus",
    9092: "Kafka",
    9100: "Node-Exporter",
    9200: "Elasticsearch",
    9300: "Elasticsearch",
    9418: "Git",
    9999: "JIRA",
    10000: "Webmin",
    10250: "Kubelet",
    11211: "Memcached",
    15672: "RabbitMQ",
    16379: "Redis",
    27017: "MongoDB",
    27018: "MongoDB",
    27019: "MongoDB",
    28017: "MongoDB",
    32608: "Kubernetes"
}


# Vulnerabilidades comuns por serviço
VULNERABILITIES = {
    "SSH": ["CVE-2016-0777", "CVE-2016-0778", "CVE-2018-15473"],
    "SMB": ["EternalBlue", "SMBGhost", "EternalRomance", "SambaCry"],
    "RDP": ["BlueKeep", "CVE-2019-0708", "CVE-2019-1181", "CVE-2019-1182"],
    "Redis": ["Unauthenticated Access", "CVE-2015-4335", "CVE-2016-8339"],
    "MongoDB": ["Unauthenticated Access", "CVE-2016-6494"],
    "Elasticsearch": ["CVE-2015-1427", "CVE-2015-3337", "CVE-2015-5531"],
    "Memcached": ["DRDoS Amplification", "CVE-2016-8704", "CVE-2016-8705"],
    "Docker": ["CVE-2019-5736", "CVE-2019-13139", "CVE-2019-14271"],
    "Kubernetes": ["CVE-2018-1002105", "CVE-2019-11253", "CVE-2019-11255"],
    "VNC": ["CVE-2006-2369", "CVE-2015-5239", "CVE-2018-20019"],
    "Jenkins": ["CVE-2017-1000353", "CVE-2018-1000861", "CVE-2019-1003000"],
    "MySQL": ["CVE-2016-6662", "CVE-2016-6663", "CVE-2016-6664"],
    "PostgreSQL": ["CVE-2019-9193", "CVE-2018-1058", "CVE-2016-5423"],
    "Oracle": ["CVE-2012-1675", "CVE-2012-3137", "CVE-2018-3110"],
    "MSSQL": ["CVE-2019-1068", "CVE-2018-8273", "CVE-2018-8271"],
}

@dataclass
class ServiceInfo:
    """Informações detalhadas sobre um serviço."""
    name: str
    version: Optional[str] = None
    ssl: bool = False
    ssl_info: Optional[Dict[str, Any]] = None
    banner: Optional[str] = None
    vulns: List[str] = field(default_factory=list)  # Alterado para List[str]
    cpe: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0  # Nível de confiança na identificação (0.0 a 1.0)
    last_checked: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário."""
        return {
            "name": self.name,
            "version": self.version,
            "ssl": self.ssl,
            "ssl_info": self.ssl_info,
            "banner": self.banner,
            "vulns": self.vulns,
            "cpe": self.cpe,
            "confidence": self.confidence,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None
        }

@dataclass
class PortScanResult:
    port: int
    protocol: str = "tcp"
    status: str = "closed"
    target: Optional[str] = None
    service: Optional[ServiceInfo] = None
    banner: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário."""
        result = {
            "port": self.port,
            "protocol": self.protocol,
            "status": self.status,
            "banner": self.banner,
            "timestamp": self.timestamp,
        }
        
        if self.service:
            service_info = {
                "name": self.service.name,
                "version": self.service.version,
                "ssl": self.service.ssl,
                "vulnerabilities": self.service.vulns,
                "cpe": self.service.cpe,
                "extra": self.service.extra,
            }
            if self.service.ssl_info:
                service_info["ssl_info"] = self.service.ssl_info
            
            result["service"] = service_info
            
        return result

    def to_json(self) -> str:
        """Retorna uma representação JSON do resultado."""
        return json.dumps(self.to_dict(), indent=2)

class PortScanner:
    """Execução assíncrona de port scanning com detecção avançada de serviços."""

    def __init__(
        self,
        target: str,
        profile: str = "quick",
        concurrency: int = 200,
        timeout: float = 2.0,
        stealth_level: int = 0,
        resolve_services: bool = True,
        check_vulns: bool = True,
    ):
        self.target = target
        self.profile = profile if profile in PROFILES else "quick"
        self.stealth_level = max(0, min(stealth_level, 5))
        self.resolve_services = resolve_services
        self.check_vulns = check_vulns
        
        # Ajusta concorrência baseado no nível de stealth
        stealth_factors = [1.0, 0.8, 0.6, 0.4, 0.2, 0.1]
        adjusted_concurrency = int(concurrency * stealth_factors[self.stealth_level])
        self.concurrency = max(10, min(adjusted_concurrency, 500))
        
        # Ajusta timeout baseado no nível de stealth
        self.timeout = timeout * (1 + (self.stealth_level * 0.5))
        
        # Resolvedor DNS assíncrono
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = 2.0
        self.resolver.lifetime = 2.0

    async def scan(self) -> List[PortScanResult]:
        """Executa a varredura de portas de forma assíncrona."""
        console.print(f"[bold]🔍 Iniciando varredura em {self.target}[/bold]")
        ports = sorted(PROFILES[self.profile])
        total_ports = len(ports)
        console.print(f"📊 Perfil: [bold]{self.profile}[/bold], Portas a verificar: [bold]{total_ports}[/bold]")
        
        if self.stealth_level > 0:
            console.print(f"🔒 Modo furtivo: nível {self.stealth_level}")
        
        results: List[PortScanResult] = []
        sem = asyncio.Semaphore(self.concurrency)
        
        # Barra de progresso
        with console.status("[bold]Verificando portas...") as status:
            async def scan_port(port: int) -> PortScanResult:
                async with sem:
                    try:
                        return await self._probe_port(port)
                    except Exception as e:
                        logger.debug(f"Erro ao escanear porta {port}: {str(e)}")
                        return PortScanResult(port=port, status="error", target=self.target)
            
            # Executa as tarefas em lote para evitar sobrecarga de memória
            batch_size = min(100, max(10, self.concurrency * 2))
            for i in range(0, len(ports), batch_size):
                batch = ports[i:i + batch_size]
                tasks = [scan_port(port) for port in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
                
                # Atualiza status
                open_ports = len([r for r in results if r.status == "open"])
                status.update(f"[bold]Verificando portas... {min(i + len(batch), total_ports)}/{total_ports} (abertas: {open_ports})")
        
        # Ordena os resultados por número de porta
        results.sort(key=lambda r: r.port)
        
        # Filtra e conta portas por status
        open_ports = [r for r in results if r.status == "open"]
        closed_ports = [r for r in results if r.status == "closed"]
        error_ports = [r for r in results if r.status == "error"]
        
        # Exibe resultados
        console.print("\n[bold]📊 Resultados da varredura:[/bold]")
        
        # Tabela de portas abertas
        if open_ports:
            table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            table.add_column("Porta", style="red", width=10)
            table.add_column("Status", style="green")
            table.add_column("Serviço", style="blue")
            table.add_column("Detalhes", style="yellow")
            
            for result in open_ports:
                service = result.service.name if result.service else "desconhecido"
                version = f" {result.service.version}" if result.service and result.service.version else ""
                ssl = "🔒" if result.service and result.service.ssl else ""
                vulns = f" [red]({len(result.service.vulns)} vulns)" if result.service and result.service.vulns else ""
                
                table.add_row(
                    f"{result.port}/tcp",
                    "[green]ABERTA[/green]",
                    f"[red]{service}{version}[/red] {ssl}",
                    vulns
                )
                
                # Adiciona banner se disponível
                if result.banner:
                    banner = result.banner.split('\n')[0][:80]  # Pega apenas a primeira linha e limita o tamanho
                    table.add_row("", "", f"[dim]↳ {banner}...[/dim]", "")
            
            console.print("\n[bold]🚪 Portas abertas:[/bold]")
            console.print(table)
        
        # Resumo
        console.print("\n[bold]📋 Resumo:[/bold]")
        console.print(f"  • [green]Portas abertas:[/green] {len(open_ports)}")
        console.print(f"  • [red]Portas fechadas:[/red] {len(closed_ports)}")
        if error_ports:
            console.print(f"  • [yellow]Erros:[/yellow] {len(error_ports)} porta(s) com erro")
        
        # Lista de portas abertas resumida
        if open_ports:
            open_ports_str = ", ".join(str(r.port) for r in open_ports)
            if len(open_ports_str) > 80:
                open_ports_str = open_ports_str[:77] + "..."
            console.print(f"\n🔍 Portas abertas: {open_ports_str}")
        
        return results
    
    def _print_result(self, result: PortScanResult):
        """Método mantido para compatibilidade, mas não é mais usado internamente."""
        pass    
    async def _probe_port(self, port: int) -> PortScanResult:
        """Verifica se uma porta está aberta e coleta informações do serviço."""
        result = PortScanResult(port=port, status="closed", target=self.target)
        
        # Atraso aleatório para evitar detecção
        if self.stealth_level > 0:
            import random
            await asyncio.sleep(random.uniform(0.01, 0.5) * self.stealth_level)
        
        # Portas que devem ser verificadas com TLS primeiro
        ssl_ports = {
            # HTTPS
            443,  # HTTPS padrão
            8443,  # HTTPS alternativo
            10443,  # HTTPS alternativo
            4443,   # HTTPS alternativo
            1443,   # HTTPS alternativo
            9443,   # Nginx Admin / HTTPS alternativo
            # Email seguro
            465,    # SMTPS
            993,    # IMAPS
            995,    # POP3S
            # Outros serviços seguros
            636,    # LDAPS
            853,    # DNS sobre TLS
            989,    # FTPS Data
            990,    # FTPS Control
            992,    # Telnet sobre TLS
            994,    # IRCS
            # Adicionais comuns
            5061,   # SIP-TLS
            5062,   # SIP-TLS
            5989,   # CIM XML sobre HTTPS
            832,    # NETCONF sobre TLS
            6514,   # Syslog sobre TLS
            5684,   # CoAP sobre DTLS
            8883,   # MQTT sobre SSL
            8884,   # MQTT sobre WebSocket
            8888,   # HTTP alternativo com SSL
            10000,  # Webmin
            10001,  # Webmin alternativo
            20000   # Usermin (Webmin para usuários)
        }
        
        # Portas que devem tentar obter banner via TLS
        http_ports_with_tls = {443, 8443, 10443, 4443, 9443, 10000, 10001, 20000}

        
        try:
            # Para portas SSL conhecidas, tenta TLS primeiro
            if port in ssl_ports:
                ssl_info = await self._check_ssl(port)
                if ssl_info:
                    result.status = "open"
                    service_name = self._identify_ssl_service(port, ssl_info)
                    result.service = ServiceInfo(name=service_name, ssl=True, ssl_info=ssl_info)
                    
                    # Tenta obter banner apenas para portas HTTP/HTTPS conhecidas
                    if port in http_ports_with_tls:
                        try:
                            banner = await self._get_ssl_banner(port)
                            if banner:
                                result.banner = banner
                                # Atualiza informações do serviço com base no banner
                                service_info = await self._identify_service(port, banner)
                                if service_info:
                                    result.service.name = service_info.name
                                    result.service.version = service_info.version
                                    result.service.cpe = service_info.cpe
                        except Exception as e:
                            logger.debug(f"Erro ao obter banner SSL da porta {port}: {str(e)}")
                    
                    return result

            
            # Se não for porta SSL ou falhar, tenta conexão TCP normal
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, port),
                timeout=self.timeout
            )
            
            # Se chegou aqui, a conexão TCP foi estabelecida, mas ainda não sabemos se a porta está realmente aberta
            # Vamos tentar ler o banner para confirmar
            try:
                # Lê o banner inicial (até 1024 bytes)
                banner_bytes = await asyncio.wait_for(
                    reader.read(1024),
                    timeout=self.timeout
                )
                
                # Se chegou aqui sem exceção, a porta está realmente aberta
                result.status = "open"
                
                if banner_bytes:
                    # Tenta decodificar como texto
                    try:
                        banner = banner_bytes.decode('utf-8', errors='replace').strip()
                        result.banner = banner
                        
                        # Identifica o serviço baseado no banner
                        service_info = await self._identify_service(port, banner)
                        if service_info:
                            result.service = service_info
                            
                    except UnicodeDecodeError:
                        # Se não for texto, exibe como hex
                        result.banner = f"[binary data] {banner_bytes.hex()[:100]}..."
                
                # Se a porta está aberta, verifica SSL/TLS em portas comuns (apenas se ainda não verificou)
                if result.status == "open" and port in ssl_ports and (result.service is None or not result.service.ssl):
                    try:
                        ssl_info = await self._check_ssl(port)
                        if ssl_info:
                            if result.service is None:
                                result.service = ServiceInfo(name=SERVICE_MAP.get(port, "unknown"))
                            result.service.ssl = True
                            result.service.ssl_info = ssl_info
                            # Atualiza o nome do serviço com base nas informações SSL
                            ssl_service = self._identify_ssl_service(port, ssl_info)
                            if ssl_service:
                                result.service.name = ssl_service
                    except Exception as e:
                        logger.debug(f"Erro ao verificar SSL na porta {port}: {str(e)}")
                        # Se falhar ao verificar SSL, mantém a porta como aberta mas sem informações SSL
            
            except (asyncio.TimeoutError, ConnectionResetError, OSError) as e:
                logger.debug(f"Erro ao ler banner da porta {port}: {str(e)}")
                
            finally:
                # Fecha a conexão
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception as e:
                    logger.debug(f"Erro ao fechar conexão: {str(e)}")
                    
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Porta fechada ou inacessível
            result.status = "closed"
            
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar porta {port}: {str(e)}")
            result.status = "error"
        
        # Se a porta está aberta, tenta identificar o serviço se ainda não identificado
        if result.status == "open":
            try:
                # Se tem serviço SSL mas não foi identificado corretamente
                if result.service and (not result.service.name or result.service.name == "ssl"):
                    if 'ssl_info' in locals() and ssl_info:
                        service_name = self._identify_ssl_service(port, ssl_info)
                        if service_name:
                            result.service.name = service_name
                
                # Se ainda não identificou o serviço, tenta pelo número da porta
                if not result.service and port in SERVICE_MAP:
                    result.service = ServiceInfo(name=SERVICE_MAP[port])
                
                # Verifica vulnerabilidades conhecidas para portas abertas
                if self.check_vulns and result.service:
                    result.service.vulns = self._check_known_vulns(port, result.service.name)
            except Exception as e:
                logger.error(f"Erro ao processar informações da porta {port}: {str(e)}")
                # Em caso de erro, mantém a porta como aberta mas sem informações adicionais

        
        return result
    
    async def _identify_service(self, port: int, banner: str) -> Optional[ServiceInfo]:
        """Tenta identificar o serviço rodando na porta com base no banner."""
        if not banner:
            return None
            
        banner_lower = banner.lower()
        service = ServiceInfo(name="unknown")
        
        # Verifica por padrões comuns de banners
        if "apache" in banner_lower or "httpd" in banner_lower:
            service.name = "Apache HTTP Server"
            if match := re.search(r'Apache[/\s]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:apache:http_server:{service.version}"
                
        elif "nginx" in banner_lower:
            service.name = "Nginx"
            if match := re.search(r'nginx[/\s]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:nginx:nginx:{service.version}"
                
        elif "microsoft-iis" in banner_lower or "microsoft httpapi" in banner_lower:
            service.name = "Microsoft IIS"
            if match := re.search(r'Microsoft-IIS/([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:microsoft:iis:{service.version}"
                
        elif "openbsd openssh" in banner_lower or "openssh" in banner_lower:
            service.name = "OpenSSH"
            if match := re.search(r'openssh[_-]?([0-9.]+[a-z]*)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:openbsd:openssh:{service.version}"
                
        elif "postfix" in banner_lower:
            service.name = "Postfix"
            if match := re.search(r'postfix[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:postfix:postfix:{service.version}"
                
        elif "exim" in banner_lower:
            service.name = "Exim"
            if match := re.search(r'exim[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:exim:exim:{service.version}"
                
        elif "dovecot" in banner_lower:
            service.name = "Dovecot"
            if match := re.search(r'dovecot[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:dovecot:dovecot:{service.version}"
                
        elif "proftpd" in banner_lower:
            service.name = "ProFTPD"
            if match := re.search(r'proftpd[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:proftpd:proftpd:{service.version}"
                
        elif "vsftpd" in banner_lower:
            service.name = "vsFTPd"
            if match := re.search(r'vsftpd[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:vsftpd:vsftpd:{service.version}"
                
        elif "mysql" in banner_lower:
            service.name = "MySQL"
            if match := re.search(r'([0-9.]+)[- ]*mysql', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:mysql:mysql:{service.version}"
                
        elif "postgresql" in banner_lower or 'postgres' in banner_lower:
            service.name = "PostgreSQL"
            if match := re.search(r'postgresql[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:postgresql:postgresql:{service.version}"
                
        elif "redis" in banner_lower:
            service.name = "Redis"
            if match := re.search(r'redis[\s:]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:redis:redis:{service.version}"
                
        elif "mongodb" in banner_lower:
            service.name = "MongoDB"
            if match := re.search(r'mongod?b[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:mongodb:mongodb:{service.version}"
                
        elif "microsoft sql server" in banner_lower or "sql server" in banner_lower:
            service.name = "Microsoft SQL Server"
            if match := re.search(r'sql server[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:microsoft:sql_server:{service.version}"
                
        elif "oracle" in banner_lower and "database" in banner_lower:
            service.name = "Oracle Database"
            if match := re.search(r'oracle[\s(]([0-9.]+)', banner, re.IGNORECASE):
                service.version = match.group(1)
                service.cpe = f"cpe:/a:oracle:database:{service.version}"
                
        # Se não identificou pelo banner, tenta pela porta
        if service.name == "unknown" and port in SERVICE_MAP:
            service.name = SERVICE_MAP[port]
        
        # Verifica vulnerabilidades conhecidas
        if self.check_vulns:
            service.vulns = self._check_known_vulns(port, service.name)
        
        return service if service.name != "unknown" else None
    
    def _identify_ssl_service(self, port: int, ssl_info: Dict[str, Any]) -> str:
        """Tenta identificar o serviço baseado na porta e informações SSL."""
        # Mapeia portas comuns para serviços SSL
        ssl_services = {
            443: "HTTPS",
            465: "SMTPS",
            563: "NNTPS",
            636: "LDAPS",
            853: "DNS-over-TLS",
            989: "FTPS (data)",
            990: "FTPS (control)",
            992: "Telnet over TLS/SSL",
            993: "IMAPS",
            994: "IRC over SSL",
            995: "POP3S",
            1443: "HTTPS (alt)",
            2376: "Docker TLS",
            2377: "Docker Swarm",
            3001: "HTTPS (Node.js)",
            3306: "MySQL over SSL",
            3389: "RDP over TLS",
            4000: "HTTPS (alt)",
            4001: "HTTPS (alt)",
            4002: "HTTPS (alt)",
            4003: "HTTPS (alt)",
            4004: "HTTPS (alt)",
            4005: "HTTPS (alt)",
            4006: "HTTPS (alt)",
            4007: "HTTPS (alt)",
            4008: "HTTPS (alt)",
            4009: "HTTPS (alt)",
            4433: "HTTPS (alt)",
            4443: "HTTPS (alt)",
            5000: "HTTPS (alt)",
            5001: "HTTPS (alt)",
            5002: "HTTPS (alt)",
            5003: "HTTPS (alt)",
            5004: "HTTPS (alt)",
            5005: "HTTPS (alt)",
            5006: "HTTPS (alt)",
            5007: "HTTPS (alt)",
            5008: "HTTPS (alt)",
            5009: "HTTPS (alt)",
            5432: "PostgreSQL over SSL",
            5671: "AMQPS",
            5800: "VNC over TLS",
            5901: "VNC over TLS (alt)",
            6001: "HTTPS (alt)",
            6002: "HTTPS (alt)",
            6003: "HTTPS (alt)",
            6004: "HTTPS (alt)",
            6005: "HTTPS (alt)",
            6006: "HTTPS (alt)",
            6007: "HTTPS (alt)",
            6008: "HTTPS (alt)",
            6009: "HTTPS (alt)",
            7000: "HTTPS (alt)",
            7001: "HTTPS (alt)",
            7002: "HTTPS (alt)",
            7003: "HTTPS (alt)",
            7004: "HTTPS (alt)",
            7005: "HTTPS (alt)",
            7006: "HTTPS (alt)",
            7007: "HTTPS (alt)",
            7008: "HTTPS (alt)",
            7009: "HTTPS (alt)",
            8000: "HTTPS (alt)",
            8001: "HTTPS (alt)",
            8002: "HTTPS (alt)",
            8003: "HTTPS (alt)",
            8004: "HTTPS (alt)",
            8005: "HTTPS (alt)",
            8006: "HTTPS (alt)",
            8007: "HTTPS (alt)",
            8008: "HTTPS (alt)",
            8009: "HTTPS (alt)",
            8080: "HTTPS (alt)",
            8081: "HTTPS (alt)",
            8082: "HTTPS (alt)",
            8083: "HTTPS (alt)",
            8084: "HTTPS (alt)",
            8085: "HTTPS (alt)",
            8086: "HTTPS (alt)",
            8087: "HTTPS (alt)",
            8088: "HTTPS (alt)",
            8089: "HTTPS (alt)",
            8090: "HTTPS (alt)",
            8091: "HTTPS (alt)",
            8443: "HTTPS (alt)",
            8444: "HTTPS (alt)",
            8445: "HTTPS (alt)",
            8446: "HTTPS (alt)",
            8447: "HTTPS (alt)",
            8448: "HTTPS (alt)",
            8449: "HTTPS (alt)",
            9000: "HTTPS (alt)",
            9001: "HTTPS (alt)",
            9002: "HTTPS (alt)",
            9003: "HTTPS (alt)",
            9004: "HTTPS (alt)",
            9005: "HTTPS (alt)",
            9006: "HTTPS (alt)",
            9007: "HTTPS (alt)",
            9008: "HTTPS (alt)",
            9009: "HTTPS (alt)",
            9010: "HTTPS (alt)",
            9443: "HTTPS (alt)",
            10000: "HTTPS (alt)",
            10443: "HTTPS (alt)",
            18080: "HTTPS (alt)",
            18081: "HTTPS (alt)",
            18082: "HTTPS (alt)",
            18083: "HTTPS (alt)",
            18084: "HTTPS (alt)",
            18085: "HTTPS (alt)",
            18086: "HTTPS (alt)",
            18087: "HTTPS (alt)",
            18088: "HTTPS (alt)",
            18089: "HTTPS (alt)",
            20000: "HTTPS (alt)",
            27017: "MongoDB over SSL",
            27018: "MongoDB over SSL (alt)",
            27019: "MongoDB over SSL (alt)",
            28017: "MongoDB over SSL (alt)",
            30000: "HTTPS (alt)",
            30001: "HTTPS (alt)",
            30002: "HTTPS (alt)",
            30003: "HTTPS (alt)",
            30004: "HTTPS (alt)",
            30005: "HTTPS (alt)",
            30006: "HTTPS (alt)",
            30007: "HTTPS (alt)",
            30008: "HTTPS (alt)",
            30009: "HTTPS (alt)",
            30010: "HTTPS (alt)",
            40000: "HTTPS (alt)",
            40001: "HTTPS (alt)",
            40002: "HTTPS (alt)",
            40003: "HTTPS (alt)",
            40004: "HTTPS (alt)",
            40005: "HTTPS (alt)",
            40006: "HTTPS (alt)",
            40007: "HTTPS (alt)",
            40008: "HTTPS (alt)",
            40009: "HTTPS (alt)",
            40010: "HTTPS (alt)",
            50000: "HTTPS (alt)",
            50001: "HTTPS (alt)",
            50002: "HTTPS (alt)",
            50003: "HTTPS (alt)",
            50004: "HTTPS (alt)",
            50005: "HTTPS (alt)",
            50006: "HTTPS (alt)",
            50007: "HTTPS (alt)",
            50008: "HTTPS (alt)",
            50009: "HTTPS (alt)",
            50010: "HTTPS (alt)",
            60000: "HTTPS (alt)",
            60001: "HTTPS (alt)",
            60002: "HTTPS (alt)",
            60003: "HTTPS (alt)",
            60004: "HTTPS (alt)",
            60005: "HTTPS (alt)",
            60006: "HTTPS (alt)",
            60007: "HTTPS (alt)",
            60008: "HTTPS (alt)",
            60009: "HTTPS (alt)",
            60010: "HTTPS (alt)",
        }
        
        return ssl_services.get(port, "SSL Service")
    
    async def _check_ssl(self, port: int) -> Optional[Dict[str, Any]]:
        """Verifica informações SSL/TLS da porta."""
        ssl_info = {}
        
        try:
            # Cria um contexto SSL
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Tenta conectar com SSL/TLS
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    self.target, 
                    port, 
                    ssl=ssl_context,
                    server_hostname=self.target
                ),
                timeout=self.timeout
            )
            
            # Obtém o certificado
            ssl_object = writer.get_extra_info('ssl_object')
            if ssl_object and hasattr(ssl_object, 'getpeercert'):
                cert = ssl_object.getpeercert()
                
                # Extrai informações do certificado
                if cert:
                    ssl_info = {
                        'version': ssl_object.version(),
                        'cipher': ssl_object.cipher(),
                        'compression': ssl_object.compression(),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber'),
                        'subject_alt_name': [
                            name[1] for name in cert.get('subjectAltName', [])
                            if name[0] == 'DNS'
                        ],
                        'ocsp': cert.get('OCSP', []),
                        'ca_issuers': cert.get('caIssuers', []),
                        'crl_distribution_points': cert.get('crlDistributionPoints', []),
                    }
                    
                    # Verifica se o certificado está expirado
                    from datetime import datetime
                    now = datetime.utcnow()
                    not_after = datetime.strptime(ssl_info['not_after'], '%b %d %H:%M:%S %Y %Z')
                    ssl_info['expired'] = now > not_after
                    
                    # Verifica se o certificado é auto-assinado
                    ssl_info['self_signed'] = (
                        ssl_info['issuer'] == ssl_info['subject']
                        and ssl_info['issuer'].get('organizationName', '').lower() != 'let\'s encrypt'
                    )
                    
                    # Verifica se o certificado é válido para o domínio
                    import idna
                    from socket import gethostbyname
                    
                    try:
                        hostname = idna.encode(self.target).decode('ascii')
                        ip = gethostbyname(hostname)
                        
                        # Verifica se o IP está nos subjectAltNames
                        alt_names = []
                        for name in ssl_info.get('subject_alt_name', []):
                            if name.startswith('*'):
                                # Lida com wildcards básicos
                                domain = name[2:]  # Remove o *.
                                if hostname.endswith(domain):
                                    alt_names.append(hostname)
                            else:
                                alt_names.append(name)
                        
                        ssl_info['valid_hostname'] = (
                            hostname in alt_names or
                            f'*.{hostname.split(".", 1)[1]}' in alt_names
                        )
                        
                        # Verifica se o IP está nos subjectAltNames
                        ssl_info['valid_ip'] = ip in alt_names
                        
                    except (UnicodeError, IndexError, OSError):
                        ssl_info['valid_hostname'] = False
                        ssl_info['valid_ip'] = False
            
            return ssl_info
            
        except (ssl.SSLError, asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            logger.debug(f"Erro ao verificar SSL na porta {port}: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar SSL na porta {port}: {str(e)}", exc_info=True)
            return None
            
        finally:
            if 'writer' in locals():
                writer.close()
                try:
                    await writer.wait_closed()
                except:
                    pass

    async def _get_ssl_banner(self, port: int) -> Optional[str]:
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, port, ssl=ssl_context, server_hostname=self.target),
                timeout=self.timeout
            )
            req = f"HEAD / HTTP/1.0\r\nHost: {self.target}\r\nUser-Agent: moriarty/1.0\r\nConnection: close\r\n\r\n"
            writer.write(req.encode("ascii"))
            await writer.drain()
            data = await asyncio.wait_for(reader.read(2048), timeout=self.timeout)
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()
            return data.decode("utf-8", errors="replace").strip()
        except Exception:
            return None

    
    def _check_known_vulns(self, port: int, service_name: str) -> List[str]:
        """Verifica vulnerabilidades conhecidas para o serviço na porta."""
        vulns = []
        
        # Verifica vulnerabilidades específicas do serviço
        for service, cves in VULNERABILITIES.items():
            if service.lower() in service_name.lower():
                vulns.extend(cves)
        
        # Verifica vulnerabilidades específicas da porta (apenas como informação, não como confirmação)
        if port == 22:  # SSH
            vulns.extend(["CVE-2016-0777 (verificar versão)", "CVE-2016-0778 (verificar versão)", "CVE-2018-15473 (verificar versão)"])
        elif port == 445:  # SMB
            vulns.extend(["Possível vulnerabilidade SMB - requer verificação de versão"])
        elif port == 3389:  # RDP
            vulns.extend(["Possível vulnerabilidade RDP - requer verificação de versão"])
        elif port == 27017:  # MongoDB
            vulns.extend(["Acesso não autenticado (se sem senha)"])
        elif port == 9200:  # Elasticsearch
            vulns.extend(["Possível exposição indevida - verificar configurações"])
        elif port == 11211:  # Memcached
            vulns.extend(["Possível amplificação DRDoS - verificar configuração"])
        elif port == 2375:  # Docker
            vulns.extend(["API Docker exposta - verificar autenticação"])
        elif port == 10250:  # Kubelet
            vulns.extend(["Kubelet exposto - verificar autenticação"])
        
        return list(set(vulns))  # Remove duplicatas


def format_scan_results(results: List[PortScanResult], output_format: str = "text", total_ports: Optional[int] = None) -> str:
    """Formata os resultados da varredura no formato solicitado.
    
    Args:
        results: Lista de resultados da varredura
        output_format: Formato de saída ('text' ou 'json')
        total_ports: Número total de portas verificadas (opcional)
    """
    if output_format.lower() == "json":
        return json.dumps([r.to_dict() for r in results], indent=2)
    
    # Formato de texto para saída no console
    output = []
    output.append("")
    output.append(f"[bold]Resultado da varredura de portas[/bold]")
    output.append(f"Alvo: {results[0].target if results else 'N/A'}")
    output.append(f"Portas verificadas: {total_ports if total_ports is not None else len([r for r in results if r.status != 'error'])}")
    output.append("-" * 80)
    
    # Cabeçalho da tabela
    output.append(
        f"{'PORTA':<8} {'PROTOCOLO':<10} {'STATUS':<10} {'SERVIÇO':<25} {'VULNERABILIDADES'}"
    )
    output.append("-" * 80)
    
    # Linhas da tabela
    for result in results:
        if result.status == "open":
            port = f"[green]{result.port}[/green]"
            status = "[green]ABERTA[/green]"
        elif result.status == "closed":
            port = f"[red]{result.port}[/red]"
            status = "[red]FECHADA[/red]"
        else:
            port = f"[yellow]{result.port}[/yellow]"
            status = "[yellow]ERRO[/yellow]"

            
        service = result.service.name if result.service else "desconhecido"
        version = f" {result.service.version}" if result.service and result.service.version else ""
        service_info = f"{service}{version}"
        
        if result.service and result.service.ssl:
            service_info += " 🔒"
            
        vulns = ", ".join(result.service.vulns) if result.service and result.service.vulns else "-"
        
        output.append(
            f"{port:<8} {'tcp':<10} {status:<10} {service_info:<25} {vulns}"
        )
    
    # Resumo
    open_ports = [r for r in results if r.status == "open"]
    output.append("-" * 80)
    output.append(f"Total de portas abertas: {len(open_ports)}")
    
    # Conta serviços por tipo
    services = {}
    for result in open_ports:
        if result.service:
            service_name = result.service.name
            services[service_name] = services.get(service_name, 0) + 1
    
    if services:
        output.append("\nServiços identificados:")
        for service, count in sorted(services.items()):
            output.append(f"  - {service}: {count} porta{'s' if count > 1 else ''}")
    
    # Verifica vulnerabilidades críticas
    critical_vulns = []
    for result in open_ports:
        if result.service and result.service.vulns:
            for vuln in result.service.vulns:
                if any(cve in vuln.upper() for cve in ["CVE", "MS"]):
                    critical_vulns.append((result.port, vuln))
    
    if critical_vulns:
        output.append("\n[bold red]VULNERABILIDADES CRÍTICAS ENCONTRADAS:[/bold red]")
        for port, vuln in critical_vulns:
            output.append(f"  - Porta {port}: {vuln}")
    
    return "\n".join(output)


__all__ = ["PortScanner", "PortScanResult", "format_scan_results"]
