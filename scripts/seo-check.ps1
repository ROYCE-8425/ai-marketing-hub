#!/usr/bin/env pwsh
# SEO Check Script for AI Marketing Hub
# Run from project root: .\scripts\seo-check.ps1

Param(
    [switch]$SkipBuild,
    [switch]$SkipLighthouse,
    [string]$Url = "http://localhost:5173"
)

$ErrorActionPreference = "Continue"
$script:errors = 0
$script:warnings = 0

function Write-Check($status, $message) {
    if ($status -eq "pass") { Write-Host "  ✅ $message" -ForegroundColor Green }
    elseif ($status -eq "warn") { Write-Host "  ⚠️  $message" -ForegroundColor Yellow; $script:warnings++ }
    else { Write-Host "  ❌ $message" -ForegroundColor Red; $script:errors++ }
}

Write-Host "`n🔍 AI Marketing Hub — SEO Check`n" -ForegroundColor Cyan
Write-Host ("=" * 50)

# 1. Check static SEO files
Write-Host "`n📄 Kiểm tra files SEO tĩnh:" -ForegroundColor Yellow

if (Test-Path "frontend/public/robots.txt") { Write-Check "pass" "robots.txt tồn tại" }
else { Write-Check "fail" "robots.txt THIẾU" }

if (Test-Path "frontend/public/sitemap.xml") { Write-Check "pass" "sitemap.xml tồn tại" }
else { Write-Check "fail" "sitemap.xml THIẾU" }

# 2. Check index.html SEO elements
Write-Host "`n📋 Kiểm tra index.html:" -ForegroundColor Yellow
$html = Get-Content "frontend/index.html" -Raw

if ($html -match 'lang="vi"') { Write-Check "pass" "lang=vi" }
else { Write-Check "fail" "Thiếu lang=vi" }

if ($html -match 'meta name="description"') { Write-Check "pass" "Meta description" }
else { Write-Check "fail" "Thiếu meta description" }

if ($html -match 'og:title') { Write-Check "pass" "Open Graph title" }
else { Write-Check "fail" "Thiếu og:title" }

if ($html -match 'og:description') { Write-Check "pass" "Open Graph description" }
else { Write-Check "fail" "Thiếu og:description" }

if ($html -match 'og:image') { Write-Check "pass" "Open Graph image" }
else { Write-Check "fail" "Thiếu og:image" }

if ($html -match 'twitter:card') { Write-Check "pass" "Twitter Card" }
else { Write-Check "fail" "Thiếu Twitter Card" }

if ($html -match 'canonical') { Write-Check "pass" "Canonical URL" }
else { Write-Check "fail" "Thiếu canonical URL" }

if ($html -match 'application/ld\+json') { Write-Check "pass" "JSON-LD structured data" }
else { Write-Check "fail" "Thiếu JSON-LD" }

# 3. Check packages
Write-Host "`n📦 Kiểm tra packages SEO:" -ForegroundColor Yellow
$pkg = Get-Content "frontend/package.json" -Raw | ConvertFrom-Json

if ($pkg.dependencies.'react-router-dom') { Write-Check "pass" "react-router-dom installed" }
else { Write-Check "fail" "react-router-dom THIẾU" }

if ($pkg.dependencies.'react-helmet-async') { Write-Check "pass" "react-helmet-async installed" }
else { Write-Check "fail" "react-helmet-async THIẾU" }

# 4. TypeScript check
Write-Host "`n🔧 TypeScript check:" -ForegroundColor Yellow
Push-Location frontend
$tscResult = npx tsc --noEmit 2>&1
if ($LASTEXITCODE -eq 0) { Write-Check "pass" "TypeScript biên dịch thành công" }
else { Write-Check "fail" "TypeScript có lỗi: $tscResult" }
Pop-Location

# Summary
Write-Host ("`n" + "=" * 50)
Write-Host "📊 Kết quả: $script:errors lỗi, $script:warnings cảnh báo" -ForegroundColor $(if ($script:errors -gt 0) { "Red" } else { "Green" })
if ($script:errors -eq 0) { Write-Host "🎉 SEO check PASSED!" -ForegroundColor Green }
else { Write-Host "💥 SEO check FAILED!" -ForegroundColor Red }
