# Task API

Küçük bir FastAPI görev servisi. İş kuralları `TaskService` içinde, HTTP katmanı `create_app()` ile kurulur. Üç GitHub Actions pipeline'ı farklı dallarda farklı derinlikte test çalıştırır.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Çalışma zamanı paketleri `requirements.txt` içindedir: `fastapi`, `uvicorn`, `pydantic`. Test paketleri `requirements-dev.txt` içindedir: `pytest`, `httpx2` (`TestClient` için). Geliştirme kurulumu ikisini birden indirir.

```bash
uvicorn app.main:app --reload
```

## Testler

```bash
pytest -m unit
pytest -m integration
pytest
```

Unit testler HTTP olmadan `TaskService` iş kurallarını doğrular. Integration testler `TestClient` ile `/health` ve `/tasks` uçlarını uçtan uca çağırır. Her integration testi yeni bir uygulama örneği açar, bu yüzden bellek içi depo testler arasında paylaşılmaz.

## Pipeline senaryoları

Dal adları varsayılan olarak `develop` ve `main`. Feature dalının adı sabit değildir: `feature/gorev`, `bugfix/baslik`, `ali/deneme` gibi `main` ve `develop` dışındaki her push aynı feature pipeline'ına girer.

```text
feature/*  --PR-->  develop  --PR veya merge-->  main
    |                   |                            |
 ci-feature         ci-develop                   ci-main
 yalnız unit        unit, sonra integration      unit ∥ integration, sonra smoke
```

### 1. Feature CI — `.github/workflows/ci-feature.yml`

Ne zaman çalışır:

- `develop` hedefine açılan veya güncellenen pull request
- `main` ve `develop` dışındaki bir dala push
- Elle tetikleme (`workflow_dispatch`)

Ne çalışır: bağımlılıklar `pip install -r requirements-dev.txt` ile kurulur, ardından yalnız `pytest -m unit`.

Senaryo: geliştirici `feature/filtre` dalına push eder. Pipeline birim testleri çalıştırır ve dakikalar içinde başlık doğrulama, tekrar kontrolü ve tamamlama kurallarının bozulup bozulmadığını söyler. Aynı dal `develop`'a PR açınca aynı pipeline yeniden çalışır. Integration test bu kapıda yoktur; PR geri bildirimi kısa kalsın diye HTTP katmanı develop birleşmesinden sonraya bırakılır.

### 2. Develop CI — `.github/workflows/ci-develop.yml`

Ne zaman çalışır:

- `develop` dalına push (PR merge dahil)
- Elle tetikleme

Ne çalışır: önce `unit` job'u, o yeşilse `integration` job'u. Integration, unit bitmeden başlamaz (`needs: unit`).

Senaryo: feature PR'si `develop`'a merge edilir. Push olayı bu pipeline'ı açar. Birim testler iş kurallarını, ardından entegrasyon testleri oluşturma, listeleme, tamamlama, 404 ve 409 cevaplarını doğrular. `develop` bu yüzden çalışan bir bütünleşik hat olarak kalır. Feature dalına yapılan push bu dosyayı tetiklemez.

### 3. Main CI — `.github/workflows/ci-main.yml`

Ne zaman çalışır:

- `main` dalına push
- `main` hedefine açılan pull request (genelde `develop` → `main`)
- Elle tetikleme

Ne çalışır: `unit` ve `integration` aynı anda başlar. İkisi de başarılı olunca `smoke` job'u uygulamayı ayağa kaldırıp `GET /health` cevabının `{"status":"ok"}` olduğunu kontrol eder.

Senaryo: `develop` `main`'e PR ile gelir. PR açıkken unit ve integration paralel koşar; ikisi de geçince sağlık kontrolü release kapısını kapatır. PR merge edilip `main`'e push düşünce aynı pipeline bir kez daha çalışır. Smoke, testlerin yeşil olduğu bir ağaçta sürecin gerçekten import edilip HTTP cevabı üretebildiğini ayrıca görür.

Eski bir çalıştırma aynı dalda yenisi gelince iptal edilir (`concurrency` + `cancel-in-progress`).

## Dal adını değiştirmek

Her workflow kendi `on` bloğunda dal dinler. Örneğin entegrasyon hattı `staging` olsun, release hattı `master` olsun:

`ci-develop.yml` içinde `branches: [develop]` değerini `branches: [staging]` yapın.

`ci-main.yml` içinde `branches: [main]` değerini `branches: [master]` yapın.

`ci-feature.yml` içindeki `branches-ignore` listesine bu iki adı yazın; aksi halde `staging` push'u hem feature hem develop pipeline'ını açar.

Feature hattını yalnız belirli öneklere bağlamak için `branches-ignore` yerine şunu kullanın:

```yaml
push:
  branches:
    - "feature/**"
    - "bugfix/**"
```

`workflow_dispatch` üç dosyada da durur. Dal filtresine uymayan bir branch'te Actions sekmesinden elle çalıştırılabilir.
