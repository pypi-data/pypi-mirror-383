# coding: utf-8
from .models import HttpMethod, UnavailableService, DataFetchHttpResult, DataFetchHttp
from time import perf_counter
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import overload
from urllib.parse import urlparse
import jwt
from datetime import datetime
import re

class Request(object):

    @staticmethod
    def is_valid_jwt(token: str) -> bool:
        """Verifica se uma string tem o formato de um JWT"""
        parts = token.split(".")
        if len(parts) != 3:
            return False  # Deve ter exatamente 3 partes
        
        try:
            # Apenas decodifica sem verificar a assinatura
            jwt.decode(token, options={"verify_signature": False})
            return True  # Decodificação sem erro -> é um JWT válido
        except jwt.DecodeError:
            return False  # Não é um JWT válido
        except jwt.ExpiredSignatureError:
            return True  # É um JWT, mas está expirado
        except jwt.InvalidTokenError:
            return False  # Token inválido
        
    def get_token_expiration(token: str) -> datetime | None:
        """Obtém a data de expiração (exp) de um JWT sem precisar validar a assinatura."""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})  # Decodifica sem verificar
            exp_timestamp = decoded.get("exp")  # Obtém o timestamp de expiração
            if exp_timestamp:
                return datetime.utcfromtimestamp(exp_timestamp)  # Converte para datetime
        except jwt.DecodeError:
            return None  # Token inválido

        return None  # Token sem expiração definida

    @staticmethod
    def is_valid_url(url: str) -> bool:
        parsed_url = urlparse(url)
        
        # Verifica se o esquema (scheme) é http ou https e se há um domínio válido
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return False
        
        # Regex para verificar um domínio válido
        domain_pattern = re.compile(
            r"^(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$"
        )
        
        return bool(domain_pattern.match(parsed_url.netloc))
    
    def __init__(self, base_url = "http://127.0.0.1:8000/", raise_error = False):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.endpoint_test_connection = 'test-connection'
        self.raise_error = raise_error

    def test_connection(self):
        try:
            response = requests.get(f"{self.base_url}{self.endpoint_test_connection}")
            if response.status_code == 200:
                return True
        except:
            ...

    @overload
    def fetch(self, endpoint : str, http_method : HttpMethod, data : dict = {}) -> DataFetchHttpResult:
         pass

    @overload
    def fetch(self, endpoint : str, http_method : HttpMethod) -> DataFetchHttpResult:
         pass

    @overload
    def fetch(self, data_fetch_http : DataFetchHttp) -> DataFetchHttpResult:
        pass

    def fetch(self, *args) -> DataFetchHttpResult:
        if len(args) > 1:
            if len(args) == 3:
                endpoint, http_method, data = args 
            else:
                endpoint, http_method = args
                data = {}
            data_fetch_http = DataFetchHttp("", endpoint, http_method, data)
        else:
            data_fetch_http = args[0]
   
        url = f'{self.base_url}{data_fetch_http.endpoint}'

        try:
            method = requests.get 
            if data_fetch_http.http_method == HttpMethod.POST:
                method = requests.post
            elif data_fetch_http.http_method == HttpMethod.PUT:
                method = requests.put
            elif data_fetch_http.http_method == HttpMethod.DELETE:
                method = requests.delete

            start = perf_counter()
            res = method(url, json=data_fetch_http.data, headers=self.headers)
            
            stop = perf_counter()
            delay = round(stop - start, 3)

            content = res.json() if res.headers.get("Content-Type") == "application/json" else {"text": res.text}
            if res.status_code == 200:
                return DataFetchHttpResult(name=data_fetch_http.name, success=True, content=content, status_code=res.status_code, delay=delay)
            elif res.status_code == 503:
                if self.raise_error:
                    raise UnavailableService()
                else:
                    return DataFetchHttpResult(name=data_fetch_http.name, success=False, status_code=503, content={'error': 'Database unavailable'}, delay=delay)
            return DataFetchHttpResult(name=data_fetch_http.name, success=False, content=content, status_code=res.status_code, delay=delay)
        except requests.exceptions.RequestException as e:
            stop = perf_counter()
            delay = round(stop - start, 3)
            return DataFetchHttpResult(
                name=data_fetch_http.name,
                success=False,
                content={"error": str(e)}, 
                status_code=0, 
                delay=delay
            )

    def fetch_all(self, list_data_fetch_http: list[DataFetchHttp]) -> dict[str, DataFetchHttpResult]:

        with ThreadPoolExecutor() as executor:
            results = executor.map(self.fetch, list_data_fetch_http)

        all_results = list(results)
        results_dict = {result.name: result for result in all_results}
        return results_dict 
