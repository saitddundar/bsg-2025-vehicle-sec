

# **Ödün Verilmiş EVSE Üzerinden Kalıcı Hizmet Reddi (P-DoS): OCPP'den CAN'e Saldırı Vektörünün Siber-Fiziksel Tehdit Analizi**

## **Bölüm 1: Yönetici Özeti**

### **Tehdit Genel Bakışı**

Bu rapor, kamuya açık şarj altyapısı ile güvenlik açısından kritik araç içi ağlar arasındaki boşluğu dolduran yeni ve çok aşamalı bir siber-fiziksel saldırı vektörünü tanıtmaktadır. Bu saldırı, teorik bir olasılık olarak değil, bağımsız olarak doğrulanmış güvenlik açıklarından yola çıkılarak oluşturulmuş makul bir senaryo olarak ele alınmaktadır. Tehdit, bir Elektrikli Araç Besleme Ekipmanının (EVSE) uzaktan ele geçirilmesiyle başlayıp, bağlı bir aracın fiziksel olarak çalışamaz hale getirilmesiyle sonuçlanan karmaşık bir saldırı zincirini içermektedir.

### **Saldırı Metodolojisi Özeti**

Saldırı, birbirini izleyen iki ana aşamadan oluşmaktadır: (1) Bir EVSE'nin, Açık Şarj Noktası Protokolü'nün (OCPP) güvensiz bellenim (firmware) güncelleme prosedürlerinin manipülasyonu yoluyla uzaktan ele geçirilmesi ve (2) Ele geçirilen EVSE'nin, bağlı bir aracın Kontrolör Alan Ağı (CAN) veriyoluna karşı protokol düzeyinde bir Kalıcı Hizmet Reddi (P-DoS) saldırısı başlatmak üzere silahlandırılması. Bu metodoloji, saldırganın fiziksel erişime ihtiyaç duymadan, ağ tabanlı bir zafiyeti kullanarak bir aracı tamamen etkisiz hale getirmesine olanak tanır.

### **Etki ve Sonuçlar**

Potansiyel etki, veri hırsızlığının ötesine geçerek bir aracı fiziksel olarak çalışamaz hale getirmeyi, sürücü güvenliğine doğrudan tehdit oluşturmayı, ulaşım lojistiğini aksatmayı ve elektrikli araç teknolojisine yönelik kamu güvenini sarsmayı içermektedir.1 Saldırının nihai sonucu, aracın fiziksel servis müdahalesi gerektiren ve "hard brick" olarak adlandırılabilecek kalıcı bir arıza durumuna sokulmasıdır. Bu durum, sadece bireysel kullanıcılar için değil, aynı zamanda operasyonları elektrikli araç filolarına dayanan ticari ve kamu kuruluşları için de ciddi sonuçlar doğurabilir.

### **Temel Azaltma Gereklilikleri**

Raporun ilerleyen bölümlerinde ayrıntılı olarak ele alınacak olan temel savunma stratejileri, katmanlı bir savunma (defense-in-depth) yaklaşımını vurgulamaktadır. Bu stratejiler arasında güvenli iletişim protokollerinin (örneğin, OCPP 2.0.1) benimsenmesi, zorunlu bellenim imzalama ve doğrulama mekanizmaları ve araç içi ağ saldırı tespit sistemlerinin (IDS) uygulanması yer almaktadır. Bu önlemler, saldırı zincirinin her aşamasını hedef alarak genel sistem direncini artırmayı amaçlamaktadır.

## **Bölüm 2: Birbirine Bağlı EV Şarj Ekosistemi: Saldırı Yüzeylerinin Birleşimi**

### **2.1. İletişim Protokolleri ve Güven Sınırları**

Bu karmaşık saldırı vektörünü anlamak için, temel iletişim protokollerini ve aralarındaki güven ilişkilerini incelemek esastır. Ekosistemin iki temel taşı, OCPP ve CAN veriyoludur.

**Açık Şarj Noktası Protokolü (OCPP)**, şarj istasyonları (Şarj Noktaları veya CP'ler) ile Merkezi Yönetim Sistemleri (CSMS) arasındaki iletişimi yönetmek için endüstri standardı haline gelmiştir. Bu protokol; faturalandırma, izleme, uzaktan teşhis ve kritik olarak bellenim güncellemeleri gibi temel işlevleri mümkün kılar.3 OCPP, şarj altyapısının operasyonel omurgasını oluşturur ve genellikle internet üzerinden çalışır.

**Kontrolör Alan Ağı (CAN) veriyolu** ise, bir aracın gerçek zamanlı sinir sistemi olarak işlev görür. Düzinelerce Elektronik Kontrol Ünitesini (ECU) birbirine bağlayarak frenleme, motor kontrolü, hava yastıkları ve direksiyon gibi hayati fonksiyonlar arasında anlık veri alışverişini sağlar.6 CAN protokolünün orijinal tasarımı, kapalı ve güvenilir bir ortam varsayımına dayandığından, kimlik doğrulama ve şifreleme gibi modern güvenlik özelliklerinden yoksundur. Bu durum, onu iç ağdaki herhangi bir yetkisiz mesaja karşı doğası gereği savunmasız kılan kritik bir eski güvenlik açığıdır.7

### **2.2. EVSE'nin Siber-Fiziksel Bir Eksen Noktası Olarak Konumu**

EVSE, bu ekosistemde benzersiz ve tehlikeli bir konuma sahiptir. Bilgi Teknolojileri (BT) dünyasını (internet, OCPP üzerinden bulut sunucuları) ve Operasyonel Teknolojiler (OT) dünyasını (aracın dahili kontrol ağı) birbirine bağlayan bir köprü veya "siber-fiziksel eksen" görevi görür.6 Bu mimari, farklı tehdit modellerinin tehlikeli bir kesişimini yaratır. EVSE, bir yandan internet tabanlı tehditlere (Ortadaki Adam saldırıları, sunucu zafiyetleri) maruz kalırken, diğer yandan bir aracın en kritik sistemlerine doğrudan fiziksel ve veri düzeyinde erişime sahiptir.3

Bu yapı, temel bir güvenlik ilkesi olan güven sınırlarının ihlali için zemin hazırlar. EV şarj ekosistemi, her biri farklı güvenlik duruşlarına ve varsayımlarına sahip farklı alanlardan oluşur. CSMS-EVSE bağlantısı gibi internet tabanlı bağlantılar, doğası gereği düşmanca kabul edilir ve TLS gibi güvenlik protokolleri gerektirir. Buna karşılık, araç içi CAN veriyolu, başlangıçta tüm düğümlerin otantik ve güvenilir olduğu varsayılan kapalı bir sistem olarak tasarlanmıştır.8 EVSE, bu güven sınırlarının sadece bitişik olduğu değil, aktif olarak köprülendiği noktadır. OCPP gibi bir protokol, dış dünyadan komutları kabul etmek üzere tasarlanmışken, EVSE'nin denetleyicisi bu komutları aracı doğrudan etkileyebilecek eylemlere dönüştürür.

Dolayısıyla, EVSE'nin ele geçirilmesi, bu güven sınırının feci bir şekilde çökmesi anlamına gelir. Bir saldırgan, "daha az güvenilir" BT alanındaki bir zafiyeti (güvensiz OCPP) kullanarak, "yüksek düzeyde güvenilir" OT alanında (aracın CAN veriyolu) ayrıcalıklı erişim elde edebilir ve komutlar yürütebilir. Bu durum, EVSE'yi yalnızca bir hedef olarak değil, aynı zamanda benzeri görülmemiş ölçekte bir ayrıcalık yükseltme saldırısı için ideal bir vektör olarak yeniden konumlandırır. Saldırgan, uzak bir ağ konumundan bir aracın temel işlevleri üzerinde doğrudan kontrol sahibi olma yeteneği kazanır.4

## **Bölüm 3: Aşama I: OCPP Kanalı Üzerinden Sızma ve Kalıcılık**

### **3.1. OCPP Bellenim Güncellemelerindeki Sistematik Zayıflıkların Sömürülmesi**

Bu saldırının ilk aşaması, özellikle yaygın olarak kullanılan eski OCPP sürümlerinde bulunan yapısal zayıflıklara odaklanmaktadır. Özellikle OCPP 1.6j, varsayılan olarak şifrelenmemiş WebSocket iletişimlerini kullandığı için Ortadaki Adam (Man-in-the-Middle, MitM) saldırılarına karşı oldukça savunmasızdır.5 Bu sürümde, bellenim dosyaları için zorunlu, sağlam sertifika tabanlı kimlik doğrulama ve kriptografik imza doğrulama mekanizmalarının bulunmaması, bu saldırıyı mümkün kılan temel kusurdur.14 Idaho Ulusal Laboratuvarı tarafından yürütülen araştırmalar, OCPP 1.6 oturumları üzerinde başarılı MitM saldırıları ve kötü amaçlı bellenim güncellemelerinin gerçekleştirilebildiğini somut olarak göstermiştir ve bu bölümün temelini oluşturmaktadır.5

### **3.2. Saldırı Yürütme: Kötü Amaçlı Bellenim Dağıtımı**

Saldırının ilk aşamasının adım adım yürütülmesi, araştırma bulgularından elde edilen teknik ayrıntılarla zenginleştirilmiştir:

* **Adım 1: Araya Girme (Interception):** Saldırgan, EVSE ve CSMS arasındaki OCPP trafiğini pasif olarak dinlemek ve aktif olarak manipüle etmek için bir MitM konumu elde eder. Bu, genellikle EVSE'nin bağlı olduğu yerel ağın veya güvensiz bir Wi-Fi ağının ele geçirilmesiyle sağlanır.5  
* **Adım 2: Manipülasyon (Manipulation):** Saldırgan, CSMS tarafından gönderilen meşru bir UpdateFirmware.req komutunu yakalar. Bu komutun içindeki URL parametresini, kötü amaçlı bellenimi barındıran ve saldırganın kontrolü altındaki bir sunucunun adresiyle değiştirir.5  
* **Adım 3: Kurulum (Installation):** EVSE, imza doğrulama mekanizmasından yoksun olduğu için, manipüle edilmiş komutu meşru kabul eder. Saldırganın sunucusuna bağlanır, kötü amaçlı bellenimi indirir ve bunu geçerli bir güncelleme olarak kurar. Bu eylem, STRIDE modeline göre doğrudan bir **Kurcalama (Tampering)** eylemidir.4 Bu tür bir zafiyetin uzaktan kod yürütmeye (Remote Code Execution) yol açabileceği birden fazla kaynakta açıkça belirtilmiştir.4

### **3.3. Gizli Kalıcılık Sağlama ("Zombi" EVSE)**

Sömürü sonrası aşamada, kötü amaçlı bellenim (bir rootkit), gizlilik ve kalıcılık için tasarlanmalıdır. CSMS tarafından tespit edilmekten kaçınmak için Heartbeat.req mesajlarına yanıt vermek ve meşru şarj oturumlarını işlemek gibi tüm normal EVSE işlevlerini taklit etmesi gerekir.4 Bellenim, kötü amaçlı yükünü etkinleştirmeden önce belirli bir tetikleyiciyi (bir aracın fiziksel olarak bağlanması ve bir şarj el sıkışmasının başlatılması) bekleyerek uykuda kalır.

Bu noktada, saldırının ölçeği tek bir cihazın ötesine geçebilir. Kullanıcının senaryosu tek bir EVSE'nin ele geçirilmesini açıklasa da, satıcı bulutları ve CSMS'lerin yüzlerce veya binlerce şarj cihazını yönettiği bilinmektedir.11 Arka uç CSMS'nin kendisinin ele geçirilmesi, bilinen bir tehdit vektörüdür.14 Bir saldırgan CSMS'yi ele geçirirse, artık yerel bir MitM saldırısına ihtiyacı kalmaz. CSMS'nin meşru ve güvenilir kanalını kullanarak kötü amaçlı bellenim güncellemesini *tüm şarj cihazı ağına* aynı anda gönderebilir.

Bu durum, tehdidi yerel ve münferit araçlara yönelik bir saldırıdan, sistemik ve potansiyel olarak feci bir olaya dönüştürür. Bir saldırgan, coğrafi olarak dağıtılmış devasa bir "zombi" EVSE botneti oluşturabilir. Bu botnet, komut üzerine tüm kurumsal veya devlet araç filolarını devre dışı bırakmak için kullanılabilir. Hatta, şarj oturumlarını koordine ederek şebeke yükünü manipüle etme potansiyeli taşır ve bu da ulusal altyapıya yönelik ciddi bir tehdit oluşturur.2

## **Bölüm 4: Aşama II: Araç İçi Ağın Bozulması için EVSE'nin Silahlandırılması**

### **4.1. CAN Veriyolu Arbitrasyon Mekanizması: Protokol Düzeyinde Bir Zafiyet**

Saldırının ikinci ve en yıkıcı aşamasını anlamak için, CAN veriyolu arbitrasyon (tahkim) sürecinin teknik temellerini kavramak zorunludur. CAN protokolü, fiziksel katmanda baskın (dominant, mantıksal 0\) ve çekinik (recessive, mantıksal 1\) bitler kullanır. Veriyolu, "kablolu-VE" (wired-AND) mantığına göre çalışır; yani, herhangi bir düğüm baskın bir bit gönderdiğinde tüm veriyolu baskın duruma geçer.18

Bu mekanizmanın en kritik sonucu, birden fazla düğümün aynı anda iletime başlaması durumunda, sayısal olarak en düşük ID'ye (kimlik) sahip mesajı gönderen düğümün her zaman arbitrasyonu kazanmasıdır. Bunun nedeni, düşük ID'lerin ikili gösteriminde daha fazla baştaki 0 (baskın) bitine sahip olması ve bu baskın bitlerin, diğer düğümlerin 1 (çekinik) bitlerini geçersiz kılmasıdır.20 Bu tahrip edici olmayan, öncelik tabanlı mekanizma, protokolün temel bir özelliği olmakla birlikte, aynı zamanda temel bir kusurudur.

### **4.2. Saldırı Yürütme: Öncelik Seli ile P-DoS**

Bu bölüm, araca yönelik saldırının anlık ve ayrıntılı bir analizini sunar:

* **Tetikleyicinin Etkinleştirilmesi:** EVSE'deki kötü amaçlı bellenim, bir aracın fiziksel olarak bağlandığını ve bir iletişim el sıkışmasının (örneğin, CCS için Güç Hattı İletişimi \- PLC aracılığıyla) başladığını algılar.  
* **CAN'e Yönelme:** Kötü amaçlı yazılım, EVSE'nin mikrodenetleyicisinin ve normalde aracın Batarya Yönetim Sistemi (BMS) gibi ECU'larıyla meşru iletişim için kullanılan CAN alıcı-vericisinin kontrolünü ele geçirir.6  
* **Selin Başlatılması:** Saldırgan, aracın veriyoluna yüksek frekanslı bir CAN çerçevesi akışı enjekte etmeye başlar. Bu çerçeveler, mümkün olan en yüksek öncelikli ID ile özel olarak hazırlanmıştır: $0x000$.9 Bu çerçevelerin veri yükü (payload) anlamsızdır; tamamen sıfırlardan oluşabilir.  
* **Arbitrasyon Kilidi:** Saldırganın $0x000$ ID'li çerçeveleri mutlak önceliğe sahip olduğundan, veriyolundaki diğer herhangi bir ECU'dan (örneğin, fren denetleyicisi ID $0x1A0$, motor kontrolü ID $0x2B0$) gelen herhangi bir mesaja karşı her bir arbitrasyon döngüsünü kazanacaktır. Meşru ECU'lar iletim yapmaya çalışacak, arbitrasyonu kaybedecek ve veriyolunun boşa çıkmasını beklemek üzere geri çekilecektir. Saldırgan veriyolunu sürekli olarak doldurduğu için, veriyolu *asla* boşa çıkmaz. Bu durum, diğer tüm düğümler için kalıcı bir "arbitrasyon açlığı" durumu yaratır.

### **4.3. Fiziksel Tezahür ve Sistematik Arıza**

Arbitrasyon kilidinin anlık sonucu, araç içi iletişimin tamamen çökmesidir. Kritik ECU'lar artık durum güncellemeleri, komutlar veya sensör okumaları gönderemez veya alamaz.

Bu durum, gösterge panelinde "Noel ağacı" etkisi olarak bilinen bir duruma yol açar; burada her ECU, diğerleriyle iletişim kaybı bildirdiği için tüm ana sistemlerin (ABS, motor, hava yastıkları, stabilite kontrolü) arıza ışıkları aynı anda yanar. Araç çalışamaz hale gelir. "Drive-by-wire" sistemleri (elektronik gaz, fren) tepki vermez. Araç çalışıyorsa, "limp-home" moduna geçebilir veya tamamen kapanabilir; kapalıysa, çalıştırılamaz.

Bu durum kalıcıdır. Araç, ele geçirilmiş EVSE'den ayrıldıktan sonra bile, ECU'lar çok sayıda "İletişim Kaybı" Teşhis Hata Kodu (DTC), tipik olarak U serisi kodlar kaydetmiş olacaktır. Birçok araç, bu kritik DTC'lerin özel araçlar kullanan sertifikalı bir teknisyen tarafından silinmesini gerektirir, bu da aracı etkin bir şekilde "tuğlalaştırır" (bricking).

Bu saldırının doğası, basit bir "parazit" (jamming) saldırısından daha karmaşıktır. CAN DoS saldırıları üzerine yapılan araştırmalar, bunun *protokole uyumlu* bir saldırı olduğu konusunda önemli bir ayrım yapar.20 Saldırgan, CAN standardının kurallarını ihlal etmemekte, aksine bu kuralları mantıksal ve yıkıcı sonuçlarına kadar sömürmektedir. Mağdur ECU'lardaki CAN denetleyicileri aslında mükemmel bir şekilde çalışmaktadır. Daha yüksek öncelikli bir mesajı doğru bir şekilde tespit eder, arbitrasyonu doğru bir şekilde kaybeder ve veriyolunun serbest kalmasını doğru bir şekilde beklerler. Veriyolunun kendisi, hata çerçevelerini içeren "Bus-Off" saldırısı gibi bir hata durumunda değildir.25 Bu incelik, saldırıyı protokol izleme açısından son derece gizli kılar. Hatalı biçimlendirilmiş paketler veya hata çerçeveleri arayan bir Saldırı Tespit Sistemi (IDS) hiçbir şey bulamaz. Veriyolu, bazı uç durumlarda meşru olabilecek tek bir, yüksek öncelikli düğümden gelen aşırı yüksek yük altında çalışıyor gibi görünür. Bu durum, tespiti ve savunmayı kaba kuvvetli parazit saldırılarına göre önemli ölçüde daha zor hale getirir.

## **Bölüm 5: Tehdit Analizi ve Adli Bilişim Etkileri**

### **5.1. STRIDE Tehdit Modeli Uygulaması**

Saldırının resmi bir analizini yapmak için, OCPP güvenliği üzerine yapılan mevcut araştırmalarda da uygulanan STRIDE çerçevesi kullanılmıştır.4 Aşağıdaki tablo, saldırı zincirinin her bir bileşenini bu endüstri standardı modele göre sınıflandırmaktadır. Bu yapılandırılmış yaklaşım, yalnızca anlatısal bir açıklamanın ötesine geçerek, kapsamlı ve hedefe yönelik karşı önlemlerin geliştirilmesi için gerekli olan tehditlerin resmi bir sınıflandırmasını sağlar.

| Tehdit Kategorisi (STRIDE) | Saldırı Tezahürü | İlgili Aşama | Destekleyici Kanıt |
| :---- | :---- | :---- | :---- |
| **Kurcalama (Tampering)** | Saldırgan, UpdateFirmware.req mesajındaki location parametresini değiştirir ve meşru bellenim dosyasını kötü amaçlı bir dosya ile değiştirir. | Aşama I (OCPP) | \[5, 14\] |
| **Hizmet Reddi (DoS)** | Saldırgan, aracın CAN veriyolunu en yüksek öncelikli ($0x000$) mesajlarla doldurarak tüm meşru ECU iletişimini engeller ve aracı çalışamaz hale getirir. | Aşama II (CAN) | \[9, 20\] |
| **Ayrıcalık Yükseltme** | Saldırgan, internet (OCPP) üzerinden elde ettiği sınırlı ağ erişimini, aracın fiziksel kontrol ağı (CAN) üzerinde en yüksek ayrıcalıklı erişime dönüştürür. | Aşama I'den II'ye | 4 |
| **Bilgi İfşası** | MitM konumundaki saldırgan, EVSE ve CSMS arasındaki şifrelenmemiş OCPP 1.6 trafiğini (örneğin, şarj oturumu verileri) dinleyebilir. | Aşama I (OCPP) | \[5, 28\] |
| **Kimlik Sahtekarlığı** | Saldırgan, kötü amaçlı bellenim sunucusunu, EVSE'ye meşru bir CSMS güncelleme kaynağı olarak sunar. | Aşama I (OCPP) | 5 |
| **İnkar (Repudiation)** | Saldırgan, saldırıyı anonim bir ağ konumundan yürüterek eylemlerini doğrudan kendisiyle ilişkilendirmeyi zorlaştırabilir. | Aşama I (OCPP) | 4 |

### **5.2. Dijital ve Fiziksel Adli Bilişim Kalıntıları**

Saldırı, hem araçta hem de şarj altyapısında belirgin izler bırakır. Bu kalıntıların analizi, bir olayın teşhisi ve kaynağının tespiti için kritik öneme sahiptir.

* **Araç Tarafındaki Kalıntılar:** En belirgin kanıt, ECU'ların teşhis belleklerinde bulunur. Neredeyse tüm modüllerin hata kayıtlarında, U serisi DTC'ler (İletişim Veriyolu Hataları) olarak bilinen çok sayıda "İletişim Kaybı" kaydı olacaktır. Bir telematik ünitesinden veya teşhis portundan elde edilen CAN veriyolu günlükleri, ID'si $0x000$ olan çerçeveler tarafından domine edilen ve %100'e yakın bir veriyolu yükü gösterecektir. Bu, normal operasyonel koşullarda asla görülmeyen bir anormalliktir.  
* **CSMS Tarafındaki Kalıntılar:** Sunucu günlükleri, şüpheli veya bilinmeyen bir alan adına (örneğin, attacker.com) ait bir URL içeren bir UpdateFirmware.req komutunun kaydını içerecektir. Saldırganın MitM konumundan kaynaklanan anormal ağ trafiği modelleri de tespit edilebilir.  
* **EVSE Tarafındaki Kalıntılar:** Birincil kanıt, bellenimin kendisidir. Fiziksel bir inceleme, bellenimin EVSE'nin mikrodenetleyicisinden dökülmesini ve karma değerinin (hash value) üreticinin resmi karma değeriyle karşılaştırılmasını gerektirir. Kötü amaçlı bellenim eşleşmeyecektir. EVSE'de tutulan ağ günlükleri (eğer varsa), saldırganın sunucusuna yapılan bağlantıları gösterebilir.

## **Bölüm 6: Karşı Önlemler ve Stratejik Azaltma**

### **6.1. Altyapının Güvenliğini Sağlama (OCPP Kanalı)**

Saldırı zincirinin ilk halkasını kırmak, altyapı düzeyinde sağlam güvenlik önlemleri gerektirir.

* **Acil Eylem:** MitM müdahalesini ve manipülasyonunu önlemek için tüm OCPP iletişimlerinde Taşıma Katmanı Güvenliği'nin (TLS) zorunlu kılınması esastır.4 Bu, CSMS ve EVSE arasındaki veri alışverişini şifreleyerek temel bir koruma katmanı sağlar.  
* **Stratejik Çözüm:** Sektör genelinde, önemli güvenlik geliştirmeleri sunan **OCPP 2.0.1**'in benimsenmesinin hızlandırılması gerekmektedir. Bu sürüm, sertifika tabanlı istemci tarafı kimlik doğrulaması ve imzalı bellenim dosyaları ile güvenli bellenim güncellemeleri gibi kritik özellikleri içerir.29 İmzalı bellenimler, EVSE'nin yalnızca kriptografik olarak doğrulanmış güncellemeleri kurmasını sağlayarak bu raporda açıklanan saldırı vektörünü tamamen ortadan kaldırır.  
* **Katmanlı Savunma:** Şarj sahalarında ağ segmentasyonu ve saldırı tespit sistemleri (IDS) uygulamak, bir MitM saldırısını gösteren anormal trafik modellerini izlemek için ek bir savunma katmanı sağlar.15

### **6.2. Aracın Güçlendirilmesi (CAN Veriyolu ve Ağ Geçidi)**

Altyapı güvenliği ihlal edilse bile, araç içi savunmalar saldırının başarılı olmasını önleyebilir.

* **Ağ Geçidi (Gateway) Olarak Güvenlik Duvarı:** Merkezi ağ geçidi ECU'su, katı bir güvenlik uygulama noktası olarak tasarlanmalıdır. Şarj portu gibi harici ve teşhis amaçlı olmayan arayüzlerden gelen $0x000$ gibi yüksek öncelikli mesajları engelleyen durum bilgisi olan filtreleme kuralları uygulamalıdır. Bu, EVSE'nin veriyoluna ayrıcalıklı mesajlar enjekte etmesini önler.  
* **Araç İçi Saldırı Tespit Sistemleri (IDS):** CAN veriyolunu yalnızca geçersiz paketler için değil, aynı zamanda normal davranıştan istatistiksel sapmalar için de izleyen anomali tabanlı IDS'ler dağıtılmalıdır. Bir IDS, $0x000$ ID'li mesajların yüksek frekanslı bir akışının aniden ortaya çıkmasını bir saldırı olarak algılayabilir ve potansiyel olarak EVSE ile olan bağlantıyı keserek aracı koruyabilir.10  
* **Fiziksel Katman Güvenliği:** Her bir alıcı-vericinin benzersiz analog sinyal özelliklerine dayanan ECU parmak izi gibi gelişmiş teknikler, protokole uygun olsalar bile sahte mesajları tespit etmek için araştırılabilir.33

### **6.3. Düzenleyici ve Standardizasyon Gereklilikleri**

Teknolojik çözümler, sağlam düzenleyici çerçevelerle desteklenmelidir.

* **Standartların Rolü:** **ISO/SAE 21434** ("Karayolu taşıtları — Siber güvenlik mühendisliği") gibi yeni ortaya çıkan otomotiv siber güvenlik standartlarının benimsenmesi kritik öneme sahiptir. Bu standart, araç yaşam döngüsü boyunca tasarımdan itibaren güvenlik (security-by-design) yaklaşımını zorunlu kılar.34  
* **Altyapı İçin Zorunluluklar:** EVSE üretimi ve dağıtımı için de benzer zorunlu standartlara ihtiyaç vardır. NIST gibi kuruluşların rehberliğine başvurulmalı ve parçalanmış, tescilli çözümler yerine birleşik, güvenli bir yaklaşım benimsenmelidir.17

Bu karşı önlemlerin arkasındaki kapsayıcı stratejik ilke, şarj güvenliği bağlamında da belirtilen **Sıfır Güven Mimarisi (Zero Trust Architecture, ZTA)**'dır.14 Bu saldırı, örtük bir güven zincirini sömürerek çalışır: EVSE, CSMS'den gelen (manipüle edilmiş) komuta güvenir ve aracın CAN veriyolu, kendisine fiziksel olarak bağlı olan herhangi bir cihaza örtük olarak güvenir. Sıfır Güven yaklaşımı, bu örtük güveni ortadan kaldırır. Bu bağlamda, aracın kritik kontrol ağının, şarj istasyonuna *asla* doğası gereği güvenmemesi gerektiği anlamına gelir. Özellikle bir EVSE gibi halka açık, harici bir cihazdan kaynaklanan her iletişim, araç içi ağı etkilemesine izin verilmeden önce kimlik doğrulaması, yetkilendirme ve denetimden geçmelidir. Bu, araç güvenliğinin eski "güvenilir çevre" modelinden modern, daha dirençli bir mimariye temel bir paradigma kaymasını temsil eder.

## **Bölüm 7: Sonuç ve Gelecekteki Araştırma Yönelimleri**

### **Bulguların Özeti**

Bu analizin sonuçları, açıklanan siber-fiziksel saldırının hem teknik olarak makul hem de ciddiyet açısından endişe verici olduğunu doğrulamaktadır. Sunulan tehdit modeli, yalnızca teknik olarak sağlam olmakla kalmayıp, aynı zamanda kritik ve gözden kaçırılmış bir saldırı vektörünü temsil etmektedir. Saldırının bileşenleri (OCPP MitM, CAN DoS) literatürde ayrı ayrı iyi belgelenmiş olsa da, bu raporun hazırlandığı sırada %85'ten fazla benzerliğe sahip tek bir makale bulunamamıştır; bu metin, mevcut araştırmaların değerli bir sentezidir. Kavramsal olarak en benzer araştırmalar, Idaho Ulusal Laboratuvarı tarafından OCPP MitM aracılığıyla kötü amaçlı bellenim güncellemelerini gösteren çalışma 5 ve CAN veriyolu DoS saldırıları üzerine yapılan akademik çalışmalar bütünüdür.9

### **Gelecekteki Tehdit Manzarası**

Bu spesifik DoS saldırısının ötesine bakarak, gelecekteki araştırma yönelimleri daha sofistike tehditleri içermelidir:

* **Daha Gelişmiş Yükler (Payloads):** Kötü amaçlı bellenimin yalnızca bir DoS saldırısı başlatmak yerine, belirli araç işlevlerini (örneğin, kapıları açma, frenleri devre dışı bırakma) manipüle etmek için dikkatlice hazırlanmış CAN mesajları enjekte etmesi senaryosu incelenmelidir. Bu, CAN veriyoluna keyfi komutlar gönderme kavramına atıfta bulunur.14  
* **Araçtan Şebekeye (V2G) Etkileri:** Araçların şebekeye güç geri beslemesine olanak tanıyan V2G teknolojisinin tanıtılması, saldırı yüzeyini önemli ölçüde genişletmektedir. Ele geçirilmiş bir EVSE veya araç, yerel şebeke altyapısını potansiyel olarak istikrarsızlaştırabilecek kötü amaçlı güç sinyalleri enjekte etmek için kullanılabilir.3  
* **Saldırı ve Savunmada Yapay Zeka/Makine Öğrenimi (AI/ML):** Yeni güvenlik açıklarını keşfetmek için yapay zeka güdümlü bulanıklaştırma (fuzzing) potansiyeli ve tersine, karmaşık, uyarlanabilir saldırılara karşı daha sağlam bir savunma sağlamak için makine öğrenimi tabanlı IDS'lerin kullanılması, gelecekteki araştırmaların odak noktası olmalıdır.7

Bu rapor, elektrikli araç ekosisteminin güvenliğinin, yalnızca tekil bileşenlerin değil, bu bileşenler arasındaki karmaşık etkileşimlerin ve güven ilişkilerinin anlaşılmasını gerektiren bütünsel bir zorluk olduğunu ortaya koymaktadır.

---

### **Alıntılar**

Johnson, J., Elmo II, D., Fragkos, G., Zhang, J., Rohde, K. W., & Salinas, S. C. (2023). *Disrupting EV Charging Sessions and Gaining Remote Code Execution with DoS, MITM, and Code Injection Exploits using OCPP 1.6*. Idaho National Laboratory (INL/CON-23-72329-Revision-0). 5

Kononov, V. (2025, 16 Eylül). *Electric vehicle and charging station alarm: risk of cyber attacks*. CYBEROO. 14

Hamdare, S., Brown, D. J., Jha, D. N., Aljaidi, M., Cao, Y., Kumar, S., Kharel, R., Jugran, M., & Kaiwartya, O. (2025). Cyber defense in OCPP for EV charging security risks. *International Journal of Information Security*, *24*(3). [https://doi.org/10.1007/s10207-025-01055-7](https://doi.org/10.1007/s10207-025-01055-7) 4

Zhang, M., & Masrur, A. (2025). Mitigating DoS Attacks on CAN: A Priority-Raise Approach and Its Timing Analysis. *2025 28th International Symposium on Design and Diagnostics of Electronic Circuits & Systems (DDECS)*. 18

Si, W., Starobinski, D., & Laifenfeld, M. (2016). *Protocol-Compliant DoS Attacks on CAN: Demonstration and Mitigation*. 20

#### **Alıntılanan çalışmalar**

1. Cybersecurity for Electric Vehicle Charging Infrastructure – Publications – Research \- Sandia National Laboratories, erişim tarihi Kasım 3, 2025, [https://www.sandia.gov/research/publications/details/cybersecurity-for-electric-vehicle-charging-infrastructure-2022-07-01/](https://www.sandia.gov/research/publications/details/cybersecurity-for-electric-vehicle-charging-infrastructure-2022-07-01/)  
2. Cybersecurity considerations for electric vehicle charging | Eaton, erişim tarihi Kasım 3, 2025, [https://www.eaton.com/content/dam/eaton/products/emobility/ev-charging/na-eaton-ac-charging/cybersecurity-considerations-ev-wp191002EN.pdf](https://www.eaton.com/content/dam/eaton/products/emobility/ev-charging/na-eaton-ac-charging/cybersecurity-considerations-ev-wp191002EN.pdf)  
3. Review of Electric Vehicle Charger Cybersecurity Vulnerabilities, Potential Impacts, and Defenses \- MDPI, erişim tarihi Kasım 3, 2025, [https://www.mdpi.com/1996-1073/15/11/3931](https://www.mdpi.com/1996-1073/15/11/3931)  
4. (PDF) Cyber defense in OCPP for EV charging security risks, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/publication/391952857\_Cyber\_defense\_in\_OCPP\_for\_EV\_charging\_security\_risks](https://www.researchgate.net/publication/391952857_Cyber_defense_in_OCPP_for_EV_charging_security_risks)  
5. Disrupting EV Charging Sessions and Gaining Remote Code ..., erişim tarihi Kasım 3, 2025, [https://inldigitallibrary.inl.gov/sites/sti/sti/Sort\_65949.pdf](https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_65949.pdf)  
6. Securing electric vehicle charging stations from cyber attacks \- Farnell, erişim tarihi Kasım 3, 2025, [https://si.farnell.com/cyber-security-of-ev-charging-stations-trc-ar](https://si.farnell.com/cyber-security-of-ev-charging-stations-trc-ar)  
7. (PDF) Cyber-Physical Security Trends of EV Charging Systems: A Survey \- ResearchGate, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/publication/384635414\_Cyber-Physical\_Security\_Trends\_of\_EV\_Charging\_Systems\_A\_Survey](https://www.researchgate.net/publication/384635414_Cyber-Physical_Security_Trends_of_EV_Charging_Systems_A_Survey)  
8. (PDF) Evaluation of CAN Bus Security Challenges \- ResearchGate, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/publication/340817175\_Evaluation\_of\_CAN\_Bus\_Security\_Challenges](https://www.researchgate.net/publication/340817175_Evaluation_of_CAN_Bus_Security_Challenges)  
9. Intrusion Detection in Vehicle Controller Area Network (CAN) Bus Using Machine Learning: A Comparative Performance Study \- NIH, erişim tarihi Kasım 3, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10099193/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10099193/)  
10. CAN-MIRGU: A Comprehensive CAN Bus Attack Dataset from Moving Vehicles for Intrusion Detection System Evaluation, erişim tarihi Kasım 3, 2025, [https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf](https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf)  
11. Cybersecurity for Electric Vehicle Fast-Charging Infrastructure: Preprint \- Publications, erişim tarihi Kasım 3, 2025, [https://docs.nrel.gov/docs/fy21osti/75236.pdf](https://docs.nrel.gov/docs/fy21osti/75236.pdf)  
12. Review of Electric Vehicle Charger Cybersecurity Vulnerabilities, Potential Impacts, and Defenses \- PSE Community.org, erişim tarihi Kasım 3, 2025, [https://psecommunity.org/wp-content/plugins/wpor/includes/file/2302/LAPSE-2023.12734-1v1.pdf](https://psecommunity.org/wp-content/plugins/wpor/includes/file/2302/LAPSE-2023.12734-1v1.pdf)  
13. DOE/DHS/DOT Volpe Technical Meeting on Electric ... \- ROSA P, erişim tarihi Kasım 3, 2025, [https://rosap.ntl.bts.gov/view/dot/34991/dot\_34991\_DS1.pdf](https://rosap.ntl.bts.gov/view/dot/34991/dot_34991_DS1.pdf)  
14. Electric vehicle and charging station alarm: risk of cyber attacks, erişim tarihi Kasım 3, 2025, [https://cert.cyberoo.com/en/electric-vehicle-and-charging-station-alarm-risk-of-cyber-attacks/](https://cert.cyberoo.com/en/electric-vehicle-and-charging-station-alarm-risk-of-cyber-attacks/)  
15. EV Charger Security \- Guide to Protecting Your Charging Station, erişim tarihi Kasım 3, 2025, [https://ev-lectron.com/blogs/blog/ev-charger-security-guide-to-protecting-your-charging-station](https://ev-lectron.com/blogs/blog/ev-charger-security-guide-to-protecting-your-charging-station)  
16. Security Flaws Uncovered in EV Charging Infrastructure OCPP Backends | CyberInsider, erişim tarihi Kasım 3, 2025, [https://cyberinsider.com/security-flaws-uncovered-in-ev-charging-infrastructure-ocpp-backends/](https://cyberinsider.com/security-flaws-uncovered-in-ev-charging-infrastructure-ocpp-backends/)  
17. Electric Vehicles in Focus, Part V: The Evolving Cyber Threat to EV Charging Stations, erişim tarihi Kasım 3, 2025, [https://core.verisk.com/Insights/Emerging-Issues/Articles/2023/September/Week-4/The-Cyber-Risks-of-Electric-Vehicle-Charging-Stations](https://core.verisk.com/Insights/Emerging-Issues/Articles/2023/September/Week-4/The-Cyber-Risks-of-Electric-Vehicle-Charging-Stations)  
18. Mitigating DoS Attacks on CAN: A Priority-Raise ... \- TU Chemnitz, erişim tarihi Kasım 3, 2025, [https://www.tu-chemnitz.de/informatik/CAS/publications/pdfs/Zhang2025a.pdf](https://www.tu-chemnitz.de/informatik/CAS/publications/pdfs/Zhang2025a.pdf)  
19. Fingerprinting Electronic Control Units for Vehicle Intrusion Detection \- USENIX, erişim tarihi Kasım 3, 2025, [https://www.usenix.org/system/files/conference/usenixsecurity16/sec16\_paper\_cho.pdf](https://www.usenix.org/system/files/conference/usenixsecurity16/sec16_paper_cho.pdf)  
20. Protocol-Compliant DoS Attacks on CAN ... \- Boston University, erişim tarihi Kasım 3, 2025, [https://people.bu.edu/staro/VTC\_2016.pdf](https://people.bu.edu/staro/VTC_2016.pdf)  
21. Addressing Vulnerabilities in CAN-FD: An Exploration and Security Enhancement Approach, erişim tarihi Kasım 3, 2025, [https://www.mdpi.com/2624-831X/5/2/15](https://www.mdpi.com/2624-831X/5/2/15)  
22. CAN bus arbitration technique. | Download Scientific Diagram \- ResearchGate, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/figure/CAN-bus-arbitration-technique\_fig1\_335407970](https://www.researchgate.net/figure/CAN-bus-arbitration-technique_fig1_335407970)  
23. Cybersecurity Of Electric Vehicle Smart Charging Management For Supply Chain Transport Operation \- IOSR Journal, erişim tarihi Kasım 3, 2025, [https://www.iosrjournals.org/iosr-jce/papers/Vol26-issue3/Ser-2/D2603022127.pdf](https://www.iosrjournals.org/iosr-jce/papers/Vol26-issue3/Ser-2/D2603022127.pdf)  
24. CANAttack: Assessing Vulnerabilities within Controller Area Network ..., erişim tarihi Kasım 3, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10575265/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10575265/)  
25. WeepingCAN: A Stealthy CAN Bus-off Attack \- NSF PAR, erişim tarihi Kasım 3, 2025, [https://par.nsf.gov/servlets/purl/10283597](https://par.nsf.gov/servlets/purl/10283597)  
26. WeepingCAN: A Stealthy CAN Bus-off Attack \- Network and Distributed System Security (NDSS) Symposium, erişim tarihi Kasım 3, 2025, [https://www.ndss-symposium.org/wp-content/uploads/autosec2021\_23002\_paper.pdf](https://www.ndss-symposium.org/wp-content/uploads/autosec2021_23002_paper.pdf)  
27. (PDF) Security of Electric Vehicle Charging Stations \- ResearchGate, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/publication/387115906\_Security\_of\_Electric\_Vehicle\_Charging\_Stations](https://www.researchgate.net/publication/387115906_Security_of_Electric_Vehicle_Charging_Stations)  
28. Data Security in Charging Infrastructure \- The Mobility House, erişim tarihi Kasım 3, 2025, [https://www.mobilityhouse.com/int\_en/knowledge-center/article/data-security-in-charging](https://www.mobilityhouse.com/int_en/knowledge-center/article/data-security-in-charging)  
29. Addressing Cybersecurity Risks Between EVSE and Charge Point Management Systems \- Argonne Scientific Publications, erişim tarihi Kasım 3, 2025, [https://publications.anl.gov/anlpubs/2024/09/190544.pdf](https://publications.anl.gov/anlpubs/2024/09/190544.pdf)  
30. A Hardware Performance Counter-Based Intrusion Detection System for DoS Attacks on Automotive CAN bus \- arXiv, erişim tarihi Kasım 3, 2025, [https://arxiv.org/pdf/2507.14739](https://arxiv.org/pdf/2507.14739)  
31. Fingerprinting Electronic Control Units for Vehicle Intrusion Detection \- USENIX, erişim tarihi Kasım 3, 2025, [https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/cho](https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/cho)  
32. (PDF) Identify a Spoofing Attack on an In-Vehicle CAN Bus Based on the Deep Features of an ECU Fingerprint Signal \- ResearchGate, erişim tarihi Kasım 3, 2025, [https://www.researchgate.net/publication/338710382\_Identify\_a\_Spoofing\_Attack\_on\_an\_In-Vehicle\_CAN\_Bus\_Based\_on\_the\_Deep\_Features\_of\_an\_ECU\_Fingerprint\_Signal](https://www.researchgate.net/publication/338710382_Identify_a_Spoofing_Attack_on_an_In-Vehicle_CAN_Bus_Based_on_the_Deep_Features_of_an_ECU_Fingerprint_Signal)  
33. Safeguarding the Future of Mobility: Cybersecurity Issues and Solutions for Infrastructure Associated with Electric Vehicle Charging, erişim tarihi Kasım 3, 2025, [https://www.ej-eng.org/index.php/ejeng/article/view/3249](https://www.ej-eng.org/index.php/ejeng/article/view/3249)  
34. Electric Vehicle Charging Infrastructure: Review, Cyber Security Considerations, Potential Impacts, Countermeasures, and Future Trends | Semantic Scholar, erişim tarihi Kasım 3, 2025, [https://www.semanticscholar.org/paper/4d6e5b9c1f87c518deef11b8769bbcd315dbb095](https://www.semanticscholar.org/paper/4d6e5b9c1f87c518deef11b8769bbcd315dbb095)  
    

