"""OtomaX signature service."""

import base64
import hashlib


class OtomaxSignatureService:
    """Service untuk generate signature OtomaX API."""

    @staticmethod
    def generate_transaction_signature(
        memberid: str, product: str, dest: str, refid: str, pin: str, password: str
    ) -> str:
        """Generate OtomaX transaction signature.

        Args:
            memberid: Member ID (will be converted to UPPERCASE)
            product: Product code (will be converted to UPPERCASE)
            dest: Destination phone number (original case)
            refid: Reference/Transaction ID (original case, can be numeric or alphanumeric)
            pin: Member PIN (original case)
            password: Member password (original case)

        Returns:
            str: Base64 encoded signature with URL-safe characters

        Examples:
            >>> service = OtomaxSignatureService()
            >>> service.generate_transaction_signature(
            ...     "vps",
            ...     "CLPDATA",
            ...     "081295221639",
            ...     "3040881",
            ...     "777999",
            ...     "vps777999",
            ... )
            'MsP6Aticed6s1rlEhvj4NKceFVQ'

            >>> service.generate_transaction_signature(
            ...     "vps",
            ...     "CLPDATA",
            ...     "081295221639",
            ...     "3040881LIST",
            ...     "777999",
            ...     "vps777999",
            ... )
            'pEGjrgXE0kSHupl8uSjPbODg7R4'

        Algorithm:
            1. Build raw string: OtomaX|MEMBERID|PRODUCT|dest|refid|pin|password
               - memberid and product are converted to UPPERCASE
               - Other fields maintain original case
            2. Generate SHA1 hash of raw string
            3. Base64 encode the hash
            4. Remove padding '=' characters
            5. Replace '+' with '-' and '/' with '_' for URL safety
        """
        # Build raw string with proper case handling
        raw = f"OtomaX|{memberid.upper()}|{product.upper()}|{dest}|{refid}|{pin}|{password}"

        # Generate SHA1 hash
        sha1_digest = hashlib.sha1(raw.encode()).digest()

        # Base64 encode and make URL-safe
        signature = base64.b64encode(sha1_digest).decode().rstrip("=")
        signature = signature.replace("+", "-").replace("/", "_")

        return signature

    @staticmethod
    def generate_balance_check_signature(memberid: str, pin: str, password: str) -> str:
        """Generate signature for balance check.

        Args:
            memberid: Member ID (will be converted to UPPERCASE)
            pin: Member PIN (original case)
            password: Member password (original case)

        Returns:
            str: Base64 encoded signature with URL-safe characters

        Algorithm:
            Raw string: OtomaX|CheckBalance|MEMBERID|pin|password
        """
        raw = f"OtomaX|CheckBalance|{memberid.upper()}|{pin}|{password}"
        sha1_digest = hashlib.sha1(raw.encode()).digest()
        signature = base64.b64encode(sha1_digest).decode().rstrip("=")
        signature = signature.replace("+", "-").replace("/", "_")
        return signature

    @staticmethod
    def generate_deposit_ticket_signature(
        memberid: str, pin: str, password: str, amount: str
    ) -> str:
        """Generate signature for deposit ticket.

        Args:
            memberid: Member ID (will be converted to UPPERCASE)
            pin: Member PIN (original case)
            password: Member password (original case)
            amount: Deposit amount (original case)

        Returns:
            str: Base64 encoded signature with URL-safe characters

        Algorithm:
            Raw string: OtomaX|ticket|MEMBERID|pin|password|amount
        """
        raw = f"OtomaX|ticket|{memberid.upper()}|{pin}|{password}|{amount}"
        sha1_digest = hashlib.sha1(raw.encode()).digest()
        signature = base64.b64encode(sha1_digest).decode().rstrip("=")
        signature = signature.replace("+", "-").replace("/", "_")
        return signature
