<!--
FAQPage JSON-LD Schema Template.
Усі питання — в user-voice (Скільки / Який / Чи є / Як перевірити …).
Мінімум 3 пари Q/A, рекомендовано 5-7.

Placeholders в snippet:
- {{QUESTION_N}}      — текст питання N
- {{ANSWER_N}}        — текст відповіді N
-->

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{{QUESTION_1}}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ANSWER_1}}"
      }
    },
    {
      "@type": "Question",
      "name": "{{QUESTION_2}}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ANSWER_2}}"
      }
    },
    {
      "@type": "Question",
      "name": "{{QUESTION_3}}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ANSWER_3}}"
      }
    }
  ]
}
</script>

<!-- Канонічні user-voice patterns (вибирай 3-7 під сторінку):
UK:
- "Скільки коштує {ПРОДУКТ} в Україні?"
- "Чи є {ПРОДУКТ} у наявності зараз?"
- "Який {РІК / МОДЕЛЬ / СТРОК} {ПРОДУКТУ}?"
- "Як перевірити {ПРОДУКТ} перед покупкою?"
- "Чи можна оглянути {ПРОДУКТ} на місці?"
- "Чи доставляєте {ПРОДУКТ} по Україні?"
- "Які документи потрібні при покупці {ПРОДУКТУ}?"
- "Чи легко знайти запчастини на {ПРОДУКТ}?"

RU:
- "Сколько стоит {ПРОДУКТ} в Украине?"
- "Есть ли {ПРОДУКТ} в наличии сейчас?"
- "Какой {ГОД / МОДЕЛЬ / СРОК} у {ПРОДУКТА}?"
- "Как проверить {ПРОДУКТ} перед покупкой?"

EN:
- "How much does {PRODUCT} cost?"
- "Is {PRODUCT} in stock?"
- "What is the {YEAR / MODEL / WARRANTY} for {PRODUCT}?"
- "How to inspect {PRODUCT} before buying?"
-->
