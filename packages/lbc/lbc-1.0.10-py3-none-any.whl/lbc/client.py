from .session import Session
from .models import Proxy, Search, Category, AdType, OwnerType, Sort, Region, Department, City, User, Ad
from .exceptions import DatadomeError, RequestError, NotFoundError
from .utils import build_search_payload_with_args, build_search_payload_with_url

from typing import Optional, List, Union
from curl_cffi import BrowserTypeLiteral

class Client(Session):
    def __init__(self, proxy: Optional[Proxy] = None, impersonate: BrowserTypeLiteral = None, 
                request_verify: bool = True, timeout: int = 30, max_retries: int = 5):
        """
        Initializes a Leboncoin Client instance with optional proxy, browser impersonation, and SSL verification settings.

        If no `impersonate` value is provided, a random browser type will be selected among common options.
        
        Args:
            proxy (Optional[Proxy], optional): Proxy configuration to use for the client. If provided, it will be applied to all requests. Defaults to None.
            impersonate (BrowserTypeLiteral, optional): Browser type to impersonate for requests (e.g., "firefox", "chrome", "edge", "safari", "safari_ios", "chrome_android"). If None, a random browser type will be chosen.
            request_verify (bool, optional): Whether to verify SSL certificates when sending requests. Set to False to disable SSL verification (not recommended for production). Defaults to True.
            timeout (int, optional): Maximum time in seconds to wait for a request before timing out. Defaults to 30.
            max_retries (int, optional): Maximum number of times to retry a request in case of failure (403 error). Defaults to 5.
        """
        super().__init__(proxy=proxy, impersonate=impersonate, request_verify=request_verify)
        
        self.request_verify = request_verify
        self.timeout = timeout
        self.max_retries = max_retries

    def _fetch(self, method: str, url: str, payload: Optional[dict] = None, timeout: int = 30, max_retries: int = 5) -> Union[dict, None]:
        """
        Internal method to send an HTTP request using the configured session.

        Args:
            method (str): HTTP method to use (e.g., "GET", "POST").
            url (str): Full URL of the API endpoint.
            payload (Optional[dict], optional): JSON payload to send with the request. Used for POST/PUT methods. Defaults to None.
            timeout (int, optional): Timeout for the request, in seconds. Defaults to 30.
            max_retries (int, optional): Number of times to retry the request in case of failure. Defaults to 5.

        Raises:
            DatadomeError: Raised when the request is blocked by Datadome protection (HTTP 403).
            RequestError: Raised for any other non-successful HTTP response.

        Returns:
            dict: Parsed JSON response from the server.
        """
        response = self.session.request(
            method=method,
            url=url, 
            json=payload,
            timeout=timeout,
            verify=self.request_verify,
        )
        if response.ok:
            return response.json()
        elif response.status_code == 403:
            if max_retries > 0:
                self.session = self._init_session(proxy=self._proxy, impersonate=self._impersonate, request_verify=self.request_verify) # Re-init session
                return self._fetch(method=method, url=url, payload=payload, timeout=timeout, max_retries=max_retries - 1)
            if self.proxy:
                raise DatadomeError(f"Access blocked by Datadome: your proxy appears to have a poor reputation, try to change it.")
            else:
                raise DatadomeError(f"Access blocked by Datadome: your activity was flagged as suspicious. Please avoid sending excessive requests.")
        elif response.status_code == 404 or response.status_code == 410:
            raise NotFoundError(f"Unable to find ad or user.")
        else:
            raise RequestError(f"Request failed with status code {response.status_code}.")

    def search(
        self,
        url: Optional[str] = None,
        text: Optional[str] = None,
        category: Category = Category.TOUTES_CATEGORIES,
        sort: Sort = Sort.RELEVANCE,
        locations: Optional[Union[List[Union[Region, Department, City]], Union[Region, Department, City]]] = None, 
        limit: int = 35, 
        limit_alu: int = 3, 
        page: int = 1, 
        ad_type: AdType = AdType.OFFER,
        owner_type: Optional[OwnerType] = None,
        shippable: Optional[bool] = None,
        search_in_title_only: bool = False,
        **kwargs
    ) -> Search:
        """
        Perform a classified ads search on Leboncoin with the specified criteria.

        You can either:
        - Provide a full `url` from a Leboncoin search to replicate the search directly.
        - Or use the individual parameters (`text`, `category`, `locations`, etc.) to construct a custom search.

        Args:
            url (Optional[str], optional): A full Leboncoin search URL. If provided, all other parameters will be ignored and the search will replicate the results from the URL.            
            text (Optional[str], optional): Search keywords. If None, returns all matching ads without filtering by keyword. Defaults to None.
            category (Category, optional): Category to search in. Defaults to Category.TOUTES_CATEGORIES.
            sort (Sort, optional): Sorting method for results (e.g., relevance, date, price). Defaults to Sort.RELEVANCE.
            locations (Optional[Union[List[Union[Region, Department, City]], Union[Region, Department, City]]], optional): One or multiple locations (region, department, or city) to filter results. Defaults to None.
            limit (int, optional): Maximum number of results to return. Defaults to 35.
            limit_alu (int, optional): Number of ALU (Annonces Lu / similar ads) suggestions to include. Defaults to 3.
            page (int, optional): Page number to retrieve for paginated results. Defaults to 1.
            ad_type (AdType, optional): Type of ad (offer or request). Defaults to AdType.OFFER.
            owner_type (Optional[OwnerType], optional): Filter by seller type (individual, professional, or all). Defaults to None.
            shippable (Optional[bool], optional): If True, only includes ads that offer shipping. Defaults to None.
            search_in_title_only (bool, optional): If True, search will only be performed on ad titles. Defaults to False.
            **kwargs: Additional advanced filters such as price range (`price=(min, max)`), surface area (`square=(min, max)`), property type, and more.

        Returns:
            Search: A `Search` object containing the parsed search results.
        """
        if url:
            payload = build_search_payload_with_url(
                url=url, limit=limit, page=page
            )
        else:
            payload = build_search_payload_with_args(
                text=text, category=category, sort=sort, locations=locations, 
                limit=limit, limit_alu=limit_alu, page=page, ad_type=ad_type,
                owner_type=owner_type, shippable=shippable, search_in_title_only=search_in_title_only, **kwargs
            )

        body = self._fetch(method="POST", url="https://api.leboncoin.fr/finder/search", payload=payload, timeout=self.timeout, max_retries=self.max_retries)
        return Search._build(raw=body, client=self)

    def get_user(
        self,
        user_id: str
    ) -> User:
        """
        Retrieve information about a user based on their user ID.

        This method fetches detailed user data such as their profile, professional status,
        and other relevant metadata available through the public user API.

        Args:
            user_id (str): The unique identifier of the user on Leboncoin. Usually found in the url (e.g 57f99bb6-0446-4b82-b05d-a44ea7bcd2cc).

        Returns:
            User: A `User` object containing the parsed user information.
        """
        user_data = self._fetch(method="GET", url=f"https://api.leboncoin.fr/api/user-card/v2/{user_id}/infos", timeout=self.timeout, max_retries=self.max_retries)

        pro_data = None
        if user_data.get("account_type") == "pro":
            try:
                pro_data = self._fetch(method="GET", url=f"https://api.leboncoin.fr/api/onlinestores/v2/users/{user_id}?fields=all", timeout=self.timeout, max_retries=self.max_retries)
            except NotFoundError:
                pass # Some professional users may not have a Leboncoin page.

        return User._build(user_data=user_data, pro_data=pro_data)
    
    def get_ad(
        self,
        ad_id: Union[str, int]
    ) -> Ad:
        """
        Retrieve detailed information about a classified ad using its ID.

        This method fetches the full content of an ad, including its description,
        pricing, location, and other relevant metadata made
        available through the public Leboncoin ad API.

        Args:
            ad_id (Union[str, int]): The unique identifier of the ad on Leboncoin. Can be found in the ad URL.

        Returns:
            Ad: An `Ad` object containing the parsed ad information.
        """
        body = self._fetch(method="GET", url=f"https://api.leboncoin.fr/api/adfinder/v1/classified/{ad_id}", timeout=self.timeout, max_retries=self.max_retries)

        return Ad._build(raw=body, client=self)