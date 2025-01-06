# Opis Aplikacji - WorkFlowSystem

## Wprowadzenie
WorkFlowApp to aplikacja służąca do zarządzania zamówieniami oraz produktami, zbudowana przy użyciu:


Aplikacja wykorzystuje wbudowane w Web2py mechanizmy autoryzacji i bazy danych. Użytkownicy mają różne role i uprawnienia, które determinują dostęp do funkcji aplikacji. Główne funkcjonalności obejmują zarządzanie produktami, tworzenie i edytowanie zamówień, import i eksport danych oraz przeglądanie zamówień w różnych widokach.

## Role i Uprawnienia
Aplikacja definiuje trzy role użytkowników:

| Funkcja | Admin | Manager | User |
|---------|-------|---------|------|
| Zarządzanie użytkownikami | Tak | Nie | Nie |
| Zarządzanie rolami | Tak | Nie | Nie |
| Zarządzanie produktami | Tak | Tak | Nie |
| Tworzenie zamówień | Tak | Tak | Tak |
| Edytowanie zamówień | Tak | Tak | Tylko własne |
| Usuwanie zamówień | Tak | Tak | Tylko własne |
| Import/Eksport danych | Tak | Tak | Nie |
| Przeglądanie wszystkich zamówień | Tak | Tak | Tylko własne |

## Moduły Aplikacji

### Produkty
- **Zarządzanie Produktami**: Użytkownicy z rolą Admin lub Manager mogą zarządzać produktami. Podstawowy widok zawiera listę produktów z funkcją wyszukiwania i paginacją.
- **Struktura Produktu**: Każdy produkt posiada następujące pola:
  - `id` (wymagane) - unikalny identyfikator produktu
  - `product_name` (wymagane) - nazwa produktu (max 500 znaków)
  - `internal_id` - automatycznie przydzielany podczas importu
- **Import/Export**: Obsługa importu i eksportu produktów w formacie CSV (max 2MB)
  - Format importu wymaga kolumn: `id`, `product_name`
  - Obsługa plików z kodowaniem UTF-8 (z BOM lub bez)

### Zamówienia
- **Zarządzanie Zamówieniami**: System obsługuje pełny cykl życia zamówienia z następującymi statusami:
  - `new` (nowe)
  - `in_progress` (w realizacji)
  - `completed` (zakończone)
  - `cancelled` (anulowane)
- **Struktura Zamówienia**: Każde zamówienie zawiera:
  - Wymagane pola:
    - `order_number` (unikalny)
    - `customer_name`
    - `project_name`
    - `product_list` (JSON z wybranymi produktami)
    - `status`
  - Opcjonalne pola:
    - `delivery_link`
    - `invoice_link`
    - `notes` (max 500 znaków)
- **Widoki**:
  - Widok tabelaryczny
  - Widok kanban (grupowanie po statusach)
  - Preferencje widoku zapisywane w localStorage

### Widoki Zamówień
- **Widok Tabelaryczny**:
  - Kolumny: Numer zamówienia, Klient, Projekt, Status, Akcje
  - Funkcjonalności:
    - Tooltip z listą produktów i notatkami przy nazwie klienta
    - Kolorowe oznaczenia statusów:
      - new (is-info) - Nowe
      - in_progress (is-warning) - W realizacji
      - delivered (is-success) - Dostarczone
      - invoiced (is-primary) - Zafakturowane
    - Przyciski akcji: 
      - Podgląd (modal ze szczegółami)
      - Edycja (przekierowanie do formularza)
    - Paginacja (10/25/50 elementów na stronę)

- **Widok Kanban**:
  - Grupowanie zamówień według statusów w kolumnach
  - Karty zamówień zawierają:
    - Numer zamówienia
    - Dane klienta
    - Nazwa projektu
    - Ikony z modalnymi szczegółami:
      - Lista produktów (ikona pudełka)
      - Notatki (ikona karteczki)
    - Style kart:
      - Minimalna wysokość 120px
      - Tło białe/jasnoszare
      - Separacja ikonek linią poziomą

- **Wspólne Funkcje**:
  - Filtrowanie:
    - Wyszukiwanie po tekście (min. 3 znaki)
    - Filtr statusów (dropdown)
    - Zakres dat (od-do)
  - Sortowanie (z zapamiętaniem kierunku):
    - Data utworzenia
    - Nazwa projektu
    - Nazwa klienta
  - Przełączanie widoków:
    - Przyciski Table/Kanban
    - Zapisywanie preferencji w localStorage
    - Aktualizacja URL bez przeładowania

- **Modale Szczegółów**:
  - Lista produktów:
    - Tabela z kolumnami: ID, Nazwa, Ilość
    - Możliwość zamknięcia przez:
      - Przycisk X w nagłówku
      - Kliknięcie tła
      - Klawisz ESC
  - Notatki:
    - Wyświetlanie treści notatki
    - Te same opcje zamknięcia co lista produktów

### Import i Eksport
- **Import Produktów**:
  - Format pliku: CSV/TXT z UTF-8 (z BOM lub bez)
  - Maksymalny rozmiar: 2MB
  - Wymagane kolumny: `id`, `product_name`
  - Walidacja danych:
    - Unikalne ID produktu
    - Nazwa produktu (max 255 znaków)
  - Automatyczne przydzielanie `internal_id`

- **Import Zamówień**:
  - Format pliku: CSV/TXT z UTF-8
  - Maksymalny rozmiar: 2MB
  - Wymagane kolumny:
    - `order_number` (unikalny)
    - `customer_name`
    - `project_name`
    - `product_list` (format JSON)
    - `status` (dozwolone wartości: new, in_progress, completed, cancelled)
  - Opcjonalne kolumny:
    - `delivery_link`
    - `invoice_link`
    - `notes`

- **Eksport**:
  - Generowanie plików CSV z kodowaniem UTF-8 BOM
  - Eksport wszystkich pól włącznie z datami utworzenia/modyfikacji
  - Osobne funkcje eksportu dla produktów i zamówień
  - Automatyczne pobieranie wygenerowanego pliku
  - Usuwanie pliku po pobraniu

### Wyszukiwanie i Filtrowanie
- **Wyszukiwanie Produktów**:
  - Wyszukiwanie po ID lub nazwie produktu
  - Minimalna długość zapytania: 3 znaki
  - Limit wyników: 10 produktów
  - Opóźnienie zapytań: 300ms (debounce)

- **Filtrowanie Zamówień**:
  - Wyszukiwanie tekstowe
  - Filtrowanie po statusie
  - Zakres dat (od-do)
  - Sortowanie po:
    - Dacie utworzenia
    - Nazwie projektu
    - Nazwie klienta
  - Kierunek sortowania (rosnąco/malejąco)
  - Ilość wyników na stronę (10/25/50)

### Zabezpieczenia
- **Walidacja Danych**:
  - Sprawdzanie unikalności ID produktów
  - Walidacja statusów zamówień
  - Walidacja formatów plików
  - Limity wielkości plików

- **Uprawnienia**:
  - Import/Export dostępny dla ról admin i manager
  - Logowanie wszystkich operacji importu
  - Obsługa błędów z szczegółowymi komunikatami
  - Transakcyjne operacje bazodanowe

### Modale
- **Modale**: Aplikacja wykorzystuje modale do wyświetlania szczegółowych informacji oraz formularzy. Modale są używane m.in. do importu/eksportu danych oraz wyświetlania szczegółów zamówień.

### Autoryzacja i Uwierzytelnianie
- **System Logowania**: 
  - Logowanie przy użyciu loginu i hasła
  - Automatyczne przekierowanie do dashboardu po zalogowaniu
  - Zabezpieczenie tras poprzez middleware 'auth'

- **Rejestracja Użytkowników**:
  - Wymagane pola: login, email, hasło
  - Automatyczna weryfikacja adresu email
  - Domyślna rola 'user' dla nowych użytkowników

- **Weryfikacja Email**:
  - Integracja z Brevo (dawniej Sendinblue) jako serwisem SMTP
  - Automatyczne wysyłanie maili weryfikacyjnych po rejestracji
  - Możliwość ponownego wysłania linku weryfikacyjnego
  - Konfiguracja w pliku .env:
    ```env
    MAIL_MAILER=smtp
    MAIL_HOST=smtp-relay.brevo.com
    MAIL_PORT=587
    MAIL_USERNAME=xxxxx@smtp-brevo.com
    MAIL_PASSWORD=xxxxxx
    ```

- **Zabezpieczenia**:
  - Middleware 'auth' dla chronionych tras
  - Middleware 'verified' dla tras wymagających weryfikacji email
  - Middleware 'role' do kontroli dostępu bazującego na rolach
  - Ochrona przed atakami CSRF

## Baza Danych
- **Modele**: Aplikacja korzysta z modeli Eloquent do zarządzania danymi w bazie danych. Główne modele to Product oraz Order.
- **Migracje**: Migracje bazy danych definiują strukturę tabel i relacje między nimi.
- **Seedery**: Seedery są używane do wypełniania bazy danych testowymi danymi.

### Struktura Tabel
- **Products**: Tabela przechowuje informacje o produktach, takie jak `id`, `product_name`, `created_at`, `updated_at`.
- **Orders**: Tabela przechowuje informacje o zamówieniach, takie jak `id`, `order_number`, `customer_name`, `project_name`, `product_list`, `status`, `delivery_link`, `invoice_link`, `notes`, `created_at`, `updated_at`.

## Logika Biznesowa
- **Tworzenie Zamówień**: Nowe zamówienia są tworzone z unikalnym numerem zamówienia i domyślnym statusem „new”.
- **Edycja Zamówień**: Użytkownicy mogą edytować zamówienia, zmieniając ich status, listę produktów oraz inne szczegóły.
- **Usuwanie Zamówień**: Zamówienia mogą być usuwane przez użytkowników z odpowiednimi uprawnieniami.

## Podsumowanie
Aplikacja jest kompleksowym narzędziem do zarządzania zamówieniami i produktami, z rozbudowanymi funkcjami importu/eksportu, wyszukiwania oraz zarządzania danymi. Każdy moduł aplikacji został zaprojektowany z myślą o różnych rolach użytkowników i ich uprawnieniach, co zapewnia elastyczność i bezpieczeństwo w zarządzaniu danymi.