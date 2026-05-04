from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def do_login(page: Page, email: str, password: str, login_timeout_ms: int, default_url: str) -> None:
    """
    Executa login automatico no Muzpa:
    1) abre URL base
    2) localiza campos de email/senha
    3) envia formulario
    4) aguarda URL de releases
    """
    page.goto(default_url, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    email_candidates = ["input[type='email']", "input[name='email']", "input[placeholder*='mail' i]"]
    pass_candidates = ["input[type='password']", "input[name='password']", "input[placeholder*='senha' i]"]

    email_input = None
    for selector in email_candidates:
        loc = page.locator(selector).first
        if loc.count() > 0:
            email_input = loc
            break

    pass_input = None
    for selector in pass_candidates:
        loc = page.locator(selector).first
        if loc.count() > 0:
            pass_input = loc
            break

    if email_input and pass_input:
        # Preenche credenciais vindas das variaveis de ambiente.
        email_input.fill(email)
        pass_input.fill(password)

        submit_candidates = [
            "button:has-text('Login')",
            "button:has-text('Entrar')",
            "button[type='submit']",
            "input[type='submit']",
        ]

        submitted = False
        for selector in submit_candidates:
            btn = page.locator(selector).first
            if btn.count() > 0:
                btn.click()
                submitted = True
                break

        if not submitted:
            # Fallback quando botao nao e encontrado.
            pass_input.press("Enter")

    try:
        page.wait_for_url("**/media/releases**", timeout=login_timeout_ms)
    except PlaywrightTimeoutError:
        # Se a navegacao nao confirmar, tenta voltar para pagina base.
        page.goto(default_url, wait_until="domcontentloaded")
