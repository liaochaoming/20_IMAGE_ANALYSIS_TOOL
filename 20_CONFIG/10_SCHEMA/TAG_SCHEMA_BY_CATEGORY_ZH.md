# 分類式標籤 Schema

更新時間：2026-05-06T16:32:48

## 原則

標籤必須跟著主分類走，不再全部混在同一層。

```text
primary_category -> tag_groups -> tags
```

## YOGA

- `person_count`: single_person, two_person, multi_person, unknown_person_count
- `yoga_pose`: tadasana, padottanasana_i, ardha_baddha_padmottanasana, i_makarasana, i_chaturanga_dandasana_i, svanasana_i, bhekasana, mandukasana_i, parangmukhi_mudra, sambhavi_mudra, yoni_mudra, sirsasana_i ...
- `view`: front_view, side_view, back_view, diagonal_view, top_view, unknown_view
- `image_quality`: clear, blurry, occluded, low_light, cropped_body, low_resolution
- `alignment_quality`: good_alignment, needs_review, bad_alignment
- `yoga_risk`: knee_risk, back_rounding, shoulder_risk, neck_risk, hip_risk, wrist_risk
- `usage`: reference_image, training_sample, analysis_target, favorite, reject

## LIAO_PHOTO

- `person_count`: single_person, two_person, group_photo, no_person, unknown_person_count
- `event_type`: daily_life, family, travel, work, food, portrait, document, other
- `location_type`: indoor, outdoor, home, office, restaurant, street, nature, unknown_location
- `photo_quality`: clear, blurry, low_light, overexposed, cropped, duplicate, needs_review
- `people_relation`: self, family, friend, client, unknown_people
- `usage`: archive, favorite, reference_image, analysis_target, reject

## ANATOMY

- `body_system`: skeletal_system, muscular_system, nervous_system, respiratory_system, fascial_system
- `body_part`: head, neck, shoulder, arm, elbow, wrist, hand, spine, chest, pelvis, hip, leg ...
- `muscle_group`: core, back_muscles, chest_muscles, shoulder_muscles, hip_flexors, glutes, hamstrings, quadriceps, calves
- `joint`: cervical_spine, thoracic_spine, lumbar_spine, shoulder_joint, elbow_joint, wrist_joint, hip_joint, knee_joint, ankle_joint
- `movement`: flexion, extension, rotation, lateral_flexion, abduction, adduction, internal_rotation, external_rotation
- `risk`: compression_risk, overstretch_risk, instability_risk, impingement_risk, needs_review
- `usage`: anatomy_reference, alignment_reference, risk_reference, training_sample

## INTERIOR_DESIGN

- `room_type`: living_room, bedroom, kitchen, bathroom, dining_room, study_room, entryway, balcony, commercial_space
- `design_style`: modern, minimal, japanese, scandinavian, industrial, classic, luxury, warm_natural, mixed_style
- `material`: wood, stone, tile, metal, glass, fabric, leather, paint, wallpaper
- `color_palette`: white_palette, gray_palette, black_palette, wood_tone, warm_neutral, cool_neutral, high_contrast, color_accent
- `furniture`: sofa, table, chair, bed, cabinet, shelf, island, desk, lighting_fixture
- `lighting`: natural_light, ambient_light, task_light, accent_light, indirect_light, low_light
- `usage`: design_reference, material_reference, style_reference, client_reference, favorite, reject

## 範例

```json
{
  "primary_category": "YOGA",
  "tags": {
    "person_count": "single_person",
    "yoga_pose": "tadasana",
    "view": "front_view",
    "alignment_quality": [
      "needs_review"
    ]
  }
}
```
