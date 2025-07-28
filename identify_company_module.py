
import re
from collections import defaultdict
from company_whitelist import COMPANIES, FIELD_WEIGHTS



def identify_company(
    title, content, companies=COMPANIES, field_weights=FIELD_WEIGHTS, min_score = 6, title_weight=2):
    scores = defaultdict(int)
    matched_counts = defaultdict(lambda: defaultdict(int))

    TITLE_FIELDS = {"official_names", "english_names", "nicknames", "tickers"}

    title_lower = title.lower()
    content_lower = content.lower()

    for company in companies:
        company_name = next(iter(company["official_names"]))
        keywords_with_fields = []
        for field, words in company.items():
            weight = field_weights.get(field, 1)
            for w in words:
                keywords_with_fields.append((w, field, weight))
        # 긴 단어 우선
        keywords_with_fields.sort(key=lambda x: -len(str(x[0])))

        # 제목 매칭 (TITLE_FIELDS만)
        current_title = title
        current_title_lower = title_lower
        for w, field, weight in keywords_with_fields:
            if field not in TITLE_FIELDS:
                continue
            pattern = r"(?<![\w가-힣]){}".format(re.escape(str(w)))
            
            if re.match(r"[A-Za-z]", str(w)):
                cnt = len(re.findall(pattern, current_title_lower, re.IGNORECASE))
                if cnt > 0:
                    scores[company_name] += cnt * weight * title_weight
                    matched_counts[company_name][field] += cnt
                    # 매칭된 부분을 치환 (대소문자 무시)
                    current_title_lower = re.sub(pattern, " ", current_title_lower, flags=re.IGNORECASE)
            else:
                cnt = len(re.findall(pattern, current_title))
                if cnt > 0:
                    scores[company_name] += cnt * weight * title_weight
                    matched_counts[company_name][field] += cnt
                    current_title = re.sub(pattern, " ", current_title)

        # 본문 매칭 (모든 필드)
        current_content = content
        current_content_lower = content_lower
        for w, field, weight in keywords_with_fields:
            
            pattern = r"(?<![\w가-힣]){}".format(re.escape(str(w)))
            if re.match(r"[A-Za-z]", str(w)):
                cnt = len(re.findall(pattern, current_content_lower, re.IGNORECASE))
                if cnt > 0:
                    scores[company_name] += cnt * weight
                    matched_counts[company_name][field] += cnt
                    current_content_lower = re.sub(pattern, " ", current_content_lower, flags=re.IGNORECASE)
            else:
                cnt = len(re.findall(pattern, current_content))
                if cnt > 0:
                    scores[company_name] += cnt * weight
                    matched_counts[company_name][field] += cnt
                    current_content = re.sub(pattern, " ", current_content)

    # if not scores:
    #     return "다른기업", 0, {}

    # max_score = max(scores.values())
    # best_companies = [k for k, v in scores.items() if v == max_score]

    # if max_score < min_score:
    #     return "다른기업", max_score, {}

    # if len(best_companies) > 1:
    #     return "동점", max_score, {k: matched_counts[k] for k in best_companies}
    # else:
    #     best = best_companies[0]
    #     return best, max_score, matched_counts[best]
    if not scores:
        return "다른기업", 0, {}

    max_score = max(scores.values())
    best_companies = [k for k, v in scores.items() if v == max_score]

    if max_score < min_score:
        return "다른기업", max_score, {}

    if len(best_companies) > 1:
        return "동점", max_score, {k: matched_counts[k] for k in best_companies}
    else:
        best = best_companies[0]
        fields = set(matched_counts[best].keys())
        # 만약 매칭된 필드가 모두 related_companies 또는 industry_categories 뿐이라면
        if fields and fields.issubset({"related_companies", "industry_categories"}):
            return "다른기업", max_score, {}
        
        return best, max_score, matched_counts[best]