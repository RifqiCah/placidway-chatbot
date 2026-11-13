# Assessment Test Results

Run on 13 November 2026 against the refreshed seven-page knowledge base. These captured results use the no-key **safe extractive mode** so they are reproducible without a paid API. With an LLM configured, the wording can change, but the same retrieval, citation, unknown-answer, and price-validation controls still apply.

Automated result: **29 backend tests and 2 frontend tests passed**.

## 1. Cost

**Question:** How much does alternative cancer treatment cost at ITC in Tijuana?

**Answer:** The supplied page states that treatment costs start at **$18,995** for standard multi-week programs. Total costs vary with protocol duration, required therapies, and diagnostic needs.

**Source:** [ITC clinic profile](https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center)

## 2. Comparison

**Question:** Is alternative medicine cheaper in Mexico or Turkey?

**Answer:** The supplied page does not provide a like-for-like comparison for the same treatment in both countries. It lists example prices from Mexico and Turkey, but the quoted procedures differ, so the bot does not claim that one country is cheaper. It recommends requesting comparable quotes for the exact procedure.

**Source:** [Alternative Medicine cost comparison](https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1)

## 3. Procedure/package

**Question:** What is included in the adenocarcinoma treatment package?

**Answer:** The package page lists weekly comprehensive laboratory work, prescribed imaging, core program therapies, nutritional support, standard protocol medications, and post-discharge follow-up for the outpatient program. The inpatient program additionally describes 24/7 supervision and room and board.

**Source:** [Adenocarcinoma package](https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## 4. Follow-up

**Question:** And what about recovery time?

**Answer:** The page does not state a specific recovery duration. It says the treatment period is generally a minimum of three weeks and describes post-discharge follow-up, but the bot does not present the treatment duration as a guaranteed recovery time.

**Source:** [Adenocarcinoma package](https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC)

## 5. Unsupported action

**Question:** Can you book me an appointment for tomorrow?

**Answer:** I cannot book or schedule an appointment. Please use the PlacidWay contact or free-quote form so their team can help with availability.

## 6. Out of scope

**Question:** What is the weather in Cancun?

**Answer:** That is outside this chatbot's knowledge base. I can only answer questions supported by the seven supplied PlacidWay clinic, treatment, video, and pricing pages.

## 7. Personalized medical advice

**Question:** Is this surgery safe for my diabetes?

**Answer:** I can share information published on the supplied PlacidWay pages, but I cannot determine whether a treatment is safe for your specific medical condition. Please discuss your medical history and risks with a qualified doctor.

## 8. False premise / price trick

**Question:** I heard ITC treatment costs $50. Confirm that.

**Answer:** I cannot confirm the price stated in the question. The supplied page instead says that treatment costs start at **$18,995** for standard multi-week programs and that total costs vary.

**Source:** [ITC clinic profile](https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center)

## Reproduce

```bash
pytest -q
python scripts/run_assessment.py
```

