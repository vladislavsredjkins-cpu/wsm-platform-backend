# Backend Recovery Spec — Stage 2 Normalization

## Purpose
This document defines the approved recovery target for aligning the live PostgreSQL schema with the World Strongman Platform Stage 2 backend model.

## Canonical Path
Recovery path for Stage 2: A

## Legacy Stable Tables
- athletes
- competitions
- results

## Stage 2 Target Tables

### competition_divisions
Columns:
id  
competition_id  
division_key  
format  
status  
approved_at  
live_at  
locked_at  

### competition_disciplines
Columns:
id  
competition_division_id  
order_no  
discipline_name  
discipline_mode  
time_cap_seconds  
lanes_per_heat  
track_length_meters  

### participants
Columns:
id  
competition_division_id  
athlete_id  
bib_no  
bodyweight_kg  

Constraint:
UNIQUE (competition_division_id, athlete_id)

## Frozen Tables
- discipline_results
- ranking_points

## Migration Principle
1. additive changes first  
2. data backfill  
3. destructive cleanup later
