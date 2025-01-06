# Astrolog Telegram Botu PINAR HANIM

Günlük burç yorumları ve tarot falı baktırabileceğiniz telegram botu. Botta abonelik oluşturarak otomatik burc yorumunuzu alabilirsiniz. Yorumu almak istediğiniz saati de belirleyebilirsiniz.

## Botumuzu deneyin

[Telegram_linki](https://t.me/PinarHanimBot)

## Özellikler
- **Günlük Burç Yorumları**: Tüm burçlar için günlük yorumlara erişebilirsiniz.
- **Tarot Kartı**: Rastgele tarot kartı çekebilir ve anlamını öğrenebilirsiniz.
- **Abonelik**: Günlük burç yorumlarını istediğiniz saatte otomatik olarak alın.
- **Esneklik**: Mesaj alma saatini istediğiniz şekilde ayarlayın.


## Komutlar

- `/burc burç_adı` |  Günlük burç yorumunu size gösterir.

    - `/burc akrep`
    
    - `/burc kova`

- `/tarot` | Rastgele bir tarot kartı çeker ve anlamını söyler.

- `/abonelik burç_adı` | Botta abonelik oluşturur ve günlük burç yorumlarını otomatik özel mesaj almanızı sağlar.

    - `/abonelik yengec`

- `/set saat_dakika` | Özel mesaj alacağınız saati belirler.

    - `/set 9 0` => Her gün 09:00'da günlük burç yorumu
    
    - `/set 15 39` => Her gün 15:39'da günlük burç yorumu
    
    - `/set 1100` => **YANLIŞ KULLANIM**

     - `/set 11.00` => **YANLIŞ KULLANIM**

## Kurulum ve Çalıştırma

1. **Repoyu yükleyin**
```bash
git clone [repo]
```
2. **Ana dizine gelin**
```bash
cd PinarHanimTelegram
```
3. **Gereksinimleri yükleyin**
```bash
pip install -r requirements.txt
```
4. **Çalıştırın**
```bash
python bot.py
```
    

Bot başarıyla çalıştırıldığında komutlarınızı Telegram'dan göndermeye başlayabilirsiniz.



![image](/images/burc.png)
---
![image](/images/tarot.png)
---
![image](/images/abonelik.png)
---
![image](/images/set.png)
---


## Katkıda Bulunma
1. Bu projeyi forklayın.
2. Yeni bir dal (branch) oluşturun: `git checkout -b yeni-ozellik`.
3. Değişikliklerinizi yapın ve commit edin: `git commit -m 'Yeni özellik'`.
4. Dalları birleştirmek için bir pull request gönderin.

Her türlü katkı memnuniyetle karşılanır!

## Sorun Bildirme
Bir hata fark ederseniz veya öneriniz varsa, lütfen bir [issue](https://github.com/kullaniciadi/PinarHanimBot/issues) açın.

# Teşekkürler