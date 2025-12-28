#!/usr/bin/env python3
"""
EVSE Saldırı Simülatörü
Ödün Verilmiş EVSE: OCPP Bellenim Manipülasyonu → CAN DoS Saldırısı

Bu modül .md dosyasındaki saldırı zincirini adım adım simüle eder:
1. MitM ile OCPP trafiği yakalama
2. Kötü amaçlı bellenim enjeksiyonu
3. EVSE'yi "zombi" moda geçirme
4. CAN DoS saldırısı başlatma
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
import json
import random

class EVSEState(Enum):
    """EVSE durumları"""
    NORMAL = "normal"                    # Normal çalışıyor
    MITM_INTERCEPTED = "mitm_intercepted" # MitM saldırısı altında
    COMPROMISED = "compromised"          # Kötü amaçlı bellenim yüklendi
    WEAPONIZED = "weaponized"            # Saldırıya hazır (zombi mod)
    ATTACKING = "attacking"              # Aktif CAN DoS saldırısı

class AttackStage(Enum):
    """Saldırı aşamaları (.md dosyasına göre)"""
    IDLE = "idle"
    STAGE_1_OCPP_MITM = "stage_1_ocpp_mitm"
    STAGE_1_FIRMWARE_INJECT = "stage_1_firmware_inject"
    STAGE_1_PERSISTENCE = "stage_1_persistence"
    STAGE_2_VEHICLE_CONNECTED = "stage_2_vehicle_connected"
    STAGE_2_CAN_ACCESS = "stage_2_can_access"
    STAGE_2_DOS_ATTACK = "stage_2_dos_attack"
    STAGE_2_HARD_BRICK = "stage_2_hard_brick"

class EVSEAttackSimulator:
    def __init__(self):
        self.evse_state = EVSEState.NORMAL
        self.attack_stage = AttackStage.IDLE
        
        # Saldırı parametreleri
        self.mitm_active = False
        self.firmware_compromised = False
        self.rootkit_active = False
        self.vehicle_connected = False
        self.can_access = False
        self.dos_active = False
        
        # OCPP verileri
        self.station_id = "CP001"
        self.charging = False
        self.energy = 0
        self.firmware_version = "v1.2.3"  # Normal
        self.malicious_firmware_version = "v1.2.3-rootkit"
        
        # CAN verileri
        self.can_bus_load = 0
        self.malicious_messages = 0
        self.blocked_ecus = 0
        
        # İstatistikler
        self.attack_started = None
        self.attack_duration = 0
        self.dtc_codes = []
        
        print(f"\n{'='*80}")
        print(f"🎭 EVSE SALDIRI SİMÜLATÖRÜ BAŞLATILDI")
        print(f"{'='*80}")
        print(f"Senaryo: Ödün Verilmiş EVSE → P-DoS Saldırısı")
        print(f"EVSE ID: {self.station_id}")
        print(f"Durum: {self.evse_state.value.upper()}")
        print(f"{'='*80}\n")
    
    async def execute_stage_1_mitm(self):
        """
        Aşama I: OCPP Kanalı Üzerinden Sızma
        - MitM saldırısı ile OCPP trafiğini yakala
        """
        print(f"\n{'🔴'*30}")
        print(f"🎯 AŞAMA I: OCPP SIZMA BAŞLADI")
        print(f"{'🔴'*30}\n")
        
        self.attack_stage = AttackStage.STAGE_1_OCPP_MITM
        
        print("⚡ Adım 1: MitM Konumu Elde Ediliyor...")
        await asyncio.sleep(1)
        print("   ├─ EVSE ile CSMS arasındaki trafik dinleniyor")
        print("   ├─ Protokol: WebSocket (OCPP 1.6) - ŞİFRELENMEMİŞ!")
        print("   └─ ✅ MitM konumu elde edildi")
        
        self.mitm_active = True
        self.evse_state = EVSEState.MITM_INTERCEPTED
        await asyncio.sleep(2)
        
        print("\n⚡ Adım 2: OCPP UpdateFirmware.req Komutu Yakalanıyor...")
        await asyncio.sleep(1)
        print("   ├─ CSMS → EVSE: UpdateFirmware.req")
        print("   ├─ Orijinal URL: https://legitimate-csms.com/firmware/v1.2.4.bin")
        print("   └─ ⚠️  Paket yakalandı!")
        await asyncio.sleep(2)
        
        print("\n⚡ Adım 3: URL Manipülasyonu...")
        await asyncio.sleep(1)
        print("   ├─ Orijinal: https://legitimate-csms.com/firmware/v1.2.4.bin")
        print("   ├─ Değiştirilen: https://attacker-c2.onion/malicious-rootkit.bin")
        print("   └─ 🚨 TAMPERING: Komut manipüle edildi!")
        await asyncio.sleep(2)
        
        return True
    
    async def execute_stage_1_firmware_inject(self):
        """Kötü amaçlı bellenim enjeksiyonu"""
        self.attack_stage = AttackStage.STAGE_1_FIRMWARE_INJECT
        
        print("\n⚡ Adım 4: Kötü Amaçlı Bellenim İndiriliyor...")
        await asyncio.sleep(1)
        print("   ├─ EVSE saldırgan sunucusuna bağlanıyor...")
        print("   ├─ İndirilen: malicious-rootkit.bin (2.4 MB)")
        print("   ├─ İmza doğrulama: ❌ YOK (OCPP 1.6 zafiyeti)")
        print("   └─ ✅ Kötü amaçlı bellenim indirildi")
        await asyncio.sleep(2)
        
        print("\n⚡ Adım 5: Bellenim Kurulumu...")
        await asyncio.sleep(1)
        print("   ├─ Eski bellenim: v1.2.3")
        print("   ├─ Yeni bellenim: v1.2.3-rootkit (gizli)")
        print("   ├─ EVSE yeniden başlatılıyor...")
        await asyncio.sleep(2)
        print("   └─ 🚨 Kötü amaçlı bellenim kuruldu!")
        
        self.firmware_compromised = True
        self.firmware_version = self.malicious_firmware_version
        self.evse_state = EVSEState.COMPROMISED
        await asyncio.sleep(2)
        
        return True
    
    async def execute_stage_1_persistence(self):
        """Gizli kalıcılık (Zombi EVSE)"""
        self.attack_stage = AttackStage.STAGE_1_PERSISTENCE
        
        print(f"\n{'🧟'*30}")
        print("⚡ Adım 6: Kalıcılık ve Gizlilik...")
        print(f"{'🧟'*30}\n")
        await asyncio.sleep(1)
        
        print("   📡 Rootkit Özellikleri:")
        print("   ├─ CSMS'e normal yanıtlar gönder (Heartbeat ✅)")
        print("   ├─ Normal şarj işlemlerini taklit et")
        print("   ├─ Bellenim versiyonunu gizle (v1.2.3 olarak göster)")
        print("   ├─ Tetikleyici bekle: Araç bağlantısı + Şarj başlangıcı")
        print("   └─ Komut bekleniyor: C&C sunucusundan")
        await asyncio.sleep(2)
        
        print("\n   🧟 EVSE artık 'ZOMBİ' modunda!")
        print("   └─ Dışarıdan normal görünüyor ama kontrolümüz altında")
        
        self.rootkit_active = True
        self.evse_state = EVSEState.WEAPONIZED
        await asyncio.sleep(2)
        
        print("\n✅ AŞAMA I TAMAMLANDI: EVSE Ele Geçirildi!")
        print("   └─ Bekleniyor: Araç bağlantısı...")
        await asyncio.sleep(2)
        
        return True
    
    async def execute_stage_2_vehicle_connection(self):
        """Aşama II: Araç bağlandı - Tetikleyici"""
        print(f"\n{'🚗'*30}")
        print(f"🎯 AŞAMA II: ARAÇ İÇİ AĞ BOZULMASI")
        print(f"{'🚗'*30}\n")
        
        self.attack_stage = AttackStage.STAGE_2_VEHICLE_CONNECTED
        
        print("🚗 Kurban Araç EVSE'ye Bağlandı!")
        await asyncio.sleep(1)
        print("   ├─ Araç modeli: Tesla Model 3 / BMW i4 (örnek)")
        print("   ├─ VIN: 1HGBH41JXMN109186")
        print("   ├─ PLC el sıkışması başladı (ISO 15118)")
        print("   └─ ⚠️  Rootkit tetiklendi!")
        
        self.vehicle_connected = True
        self.charging = True
        await asyncio.sleep(2)
        
        return True
    
    async def execute_stage_2_can_access(self):
        """CAN veriyoluna erişim"""
        self.attack_stage = AttackStage.STAGE_2_CAN_ACCESS
        
        print("\n⚡ CAN Veriyolu Erişimi...")
        await asyncio.sleep(1)
        print("   ├─ EVSE'nin CAN alıcı-vericisi kontrole alındı")
        print("   ├─ Hedef: Aracın BMS (Batarya Yönetim Sistemi)")
        print("   ├─ İletişim: CCS DC Fast Charge standardı")
        print("   └─ ✅ CAN veriyolu erişimi sağlandı!")
        
        self.can_access = True
        await asyncio.sleep(2)
        
        return True
    
    async def execute_stage_2_dos_attack(self):
        """Protocol-Compliant CAN DoS Saldırısı"""
        self.attack_stage = AttackStage.STAGE_2_DOS_ATTACK
        
        print(f"\n{'💀'*30}")
        print("⚡ CAN DoS SALDIRISI BAŞLATILIYOR...")
        print(f"{'💀'*30}\n")
        await asyncio.sleep(1)
        
        print("   🎯 Saldırı Parametreleri:")
        print("   ├─ Mesaj ID: 0x000 (En yüksek öncelik)")
        print("   ├─ Frekans: 1000 mesaj/saniye")
        print("   ├─ Payload: 0x00 00 00 00 00 00 00 00")
        print("   └─ Tip: Protocol-Compliant Arbitration Lock")
        await asyncio.sleep(2)
        
        self.dos_active = True
        self.evse_state = EVSEState.ATTACKING
        self.attack_started = datetime.now()
        
        print("\n   💥 SALDIRI AKTİF!")
        
        # Progresif DoS etkisi
        for i in range(5):
            await asyncio.sleep(1)
            self.can_bus_load = min(98, 20 + i * 20)
            self.malicious_messages = (i + 1) * 10
            self.blocked_ecus = min(5, i + 1)
            
            print(f"\n   [{i+1}s] Durum:")
            print(f"   ├─ Bus Yükü: {self.can_bus_load}%")
            print(f"   ├─ 0x000 Mesajlar: {self.malicious_messages}/saniye")
            print(f"   └─ Engellenen ECU: {self.blocked_ecus}/5")
        
        await asyncio.sleep(1)
        
        return True
    
    async def execute_stage_2_hard_brick(self):
        """Aracın tamamen çalışamaz hale gelmesi"""
        self.attack_stage = AttackStage.STAGE_2_HARD_BRICK
        
        print(f"\n{'💀'*30}")
        print("⚠️  ARAÇ HARD BRICK DURUMUNA GİRDİ!")
        print(f"{'💀'*30}\n")
        await asyncio.sleep(1)
        
        # DTC kodları oluştur
        self.dtc_codes = [
            "U0100: ECM İletişim Kaybı",
            "U0121: ABS İletişim Kaybı",
            "U0155: BMS İletişim Kaybı",
            "U0164: HVAC İletişim Kaybı",
            "U0195: Gateway İletişim Kaybı"
        ]
        
        print("   🚨 Araç Gösterge Paneli:")
        print("   ├─ ❌ Motor Arıza Lambası (Check Engine)")
        print("   ├─ ❌ ABS Arıza Lambası")
        print("   ├─ ❌ Hava Yastığı Arıza Lambası")
        print("   ├─ ❌ Batarya Sistemi Arıza")
        print("   └─ ❌ Güç Aktarma Arızası")
        
        await asyncio.sleep(2)
        
        print("\n   📝 DTC Hata Kodları:")
        for dtc in self.dtc_codes:
            print(f"   ├─ {dtc}")
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(2)
        
        print("\n   💀 Araç Durumu:")
        print("   ├─ Motor: ÇALIŞMIYOR")
        print("   ├─ Drive Modu: KULLANILAMAZ")
        print("   ├─ Şarj: DEVAM EDİYOR (Anomali!)")
        print("   ├─ Elektronik: TAM ARIZA")
        print("   └─ Servis: ⚠️  PROFESYONEL MÜDAHALE GEREKLİ!")
        
        await asyncio.sleep(2)
        
        self.attack_duration = (datetime.now() - self.attack_started).total_seconds()
        
        print(f"\n✅ SALDIRI TAMAMLANDI!")
        print(f"   ├─ Süre: {self.attack_duration:.1f} saniye")
        print(f"   ├─ Durum: Araç tamamen etkisiz")
        print(f"   └─ EVSE: Hala aktif, yeni kurbanlar bekliyor...")
        
        return True
    
    async def run_full_attack(self):
        """Tam saldırı zincirini çalıştır"""
        print("\n" + "="*80)
        print("🎬 TAM SALDIRI ZİNCİRİ BAŞLATILIYOR")
        print("Senaryo: OCPP → EVSE → CAN → P-DoS")
        print("="*80)
        
        await asyncio.sleep(2)
        
        # AŞAMA I: OCPP Sızma
        success = await self.execute_stage_1_mitm()
        if not success:
            return False
        
        success = await self.execute_stage_1_firmware_inject()
        if not success:
            return False
        
        success = await self.execute_stage_1_persistence()
        if not success:
            return False
        
        # Araç bağlanması için bekle (simüle)
        print("\n⏳ Kurban araç bekleniyor...")
        await asyncio.sleep(3)
        
        # AŞAMA II: Araç İçi Ağ Bozulması
        success = await self.execute_stage_2_vehicle_connection()
        if not success:
            return False
        
        success = await self.execute_stage_2_can_access()
        if not success:
            return False
        
        success = await self.execute_stage_2_dos_attack()
        if not success:
            return False
        
        success = await self.execute_stage_2_hard_brick()
        if not success:
            return False
        
        # Final rapor
        self.print_final_report()
        
        return True
    
    def print_final_report(self):
        """Final adli bilişim raporu"""
        print("\n" + "="*80)
        print("📊 ADLİ BİLİŞİM RAPORU")
        print("="*80)
        
        print("\n🎯 SALDIRI ÖZETİ:")
        print(f"   ├─ Başlangıç: {self.attack_started.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   ├─ Süre: {self.attack_duration:.1f} saniye")
        print(f"   ├─ EVSE ID: {self.station_id}")
        print(f"   └─ Bellenim: {self.firmware_version}")
        
        print("\n🔗 SALDIRI ZİNCİRİ (STRIDE Modeli):")
        print("   ├─ [Tampering] OCPP UpdateFirmware URL manipülasyonu")
        print("   ├─ [Privilege Escalation] Internet → CAN erişimi")
        print("   └─ [DoS] Protocol-Compliant CAN arbitrasyon kilidi")
        
        print("\n📡 OCPP VERİLERİ:")
        print(f"   ├─ Şarj Durumu: {'AKTİF' if self.charging else 'PASİF'}")
        print(f"   ├─ Enerji: {self.energy} Wh")
        print(f"   └─ MitM: {'✓ TESPİT EDİLDİ' if self.mitm_active else '✗'}")
        
        print("\n🚗 CAN VERİYOLU:")
        print(f"   ├─ Bus Yükü: {self.can_bus_load}%")
        print(f"   ├─ 0x000 Mesajlar: {self.malicious_messages}/saniye")
        print(f"   └─ Engellenen ECU: {self.blocked_ecus}")
        
        print("\n💀 ARAÇ DURUMU:")
        for dtc in self.dtc_codes:
            print(f"   ├─ {dtc}")
        print(f"   └─ Sonuç: HARD BRICK - Servis gerekli")
        
        print("\n🛡️  ÖNER İLEN KARŞI ÖNLEMLER:")
        print("   ├─ OCPP: TLS zorunlu + OCPP 2.0.1'e geçiş")
        print("   ├─ Bellenim: Kriptografik imza doğrulama")
        print("   ├─ CAN: Ağ geçidi güvenlik duvarı (0x000 filtrele)")
        print("   ├─ IDS: Anomali tabanlı saldırı tespit sistemi")
        print("   └─ Düzenleyici: ISO/SAE 21434 uyumluluğu")
        
        print("\n" + "="*80)
        print("⚠️  Bu simülasyon eğitim amaçlıdır!")
        print("   Gerçek sistemlerde ASLA test etmeyin!")
        print("="*80 + "\n")
    
    def get_current_state(self):
        """Mevcut durumu JSON olarak döndür (dashboard için)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'evse_state': self.evse_state.value,
            'attack_stage': self.attack_stage.value,
            'mitm_active': self.mitm_active,
            'firmware_compromised': self.firmware_compromised,
            'rootkit_active': self.rootkit_active,
            'vehicle_connected': self.vehicle_connected,
            'can_access': self.can_access,
            'dos_active': self.dos_active,
            'ocpp': {
                'station_id': self.station_id,
                'charging': self.charging,
                'energy': self.energy,
                'firmware_version': self.firmware_version
            },
            'can': {
                'bus_load': self.can_bus_load,
                'malicious_messages': self.malicious_messages,
                'blocked_ecus': self.blocked_ecus
            },
            'dtc_codes': self.dtc_codes
        }

async def main():
    simulator = EVSEAttackSimulator()
    
    print("\n🎮 Tam saldırı zinciri başlatılıyor...")
    print("   (Ctrl+C ile durdurun)\n")
    
    await asyncio.sleep(2)
    
    try:
        await simulator.run_full_attack()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simülasyon durduruldu")

if __name__ == "__main__":
    asyncio.run(main())

