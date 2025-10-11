select tn.table_name as name,
       t.relname as name_without_schema,
       t.relkind::text as kind,
       pg_size_pretty(ds.data_size) as pretty_data_size,
       ts.total_size,
       ds.data_size,
       att.all_columns,
       pk.pk_columns,
       pk.pk_types,
       d.comment,
       i.create_indexes,
       i.rename_indexes,
       chk.create_constraints as create_check_constraints,
       fk.drop_constraints,
       uni.create_constraints || fk.create_constraints as create_constraints,
       fk.validate_constraints,
       p.grant_privileges,
       tg.create_triggers,
       v.drop_views,
       v.create_views,
       v.view_acl_to_grants_params,
       v.comment_views,
       f.drop_functions,
       f.create_functions,
       f.function_acl_to_grants_params,
       att.alter_sequences,
       sp.storage_parameters,
       inh.inherits,
       attach.attach_expr,
       part.partition_expr,
       ri.replica_identity,
       pb.publications
  from pg_class t
 cross join lateral (select t.oid::regclass::text as table_name) tn
 cross join pg_relation_size(t.oid) as ds(data_size)
 cross join pg_total_relation_size(t.oid) as ts(total_size)
  left join lateral (select format('comment on table %s__tat_new is %L;',
                                   tn.table_name,
                                   d.description) as comment
                       from pg_description d
                      where d.objoid = t.oid and
                            d.objsubid = 0 and
                            d.classoid = 'pg_class'::regclass) d
         on true
 cross join lateral (select coalesce(array_agg(replace(replace(pg_get_indexdef(i.indexrelid),
                                                               ' ON ',
                                                               '__tat_new ON '),
                                                       ' USING ',
                                                       '__tat_new USING ')
                                               order by cardinality(i.indkey) desc),
                                     '{}') as create_indexes,
                            coalesce(array_agg(format('alter index %s.%s rename to %s;',
                                                      ic.relnamespace::regnamespace,
                                                      (ic.relname || '__tat_new')::name,
                                                      ic.relname)),
                                     '{}') as rename_indexes
                       from pg_index i
                      inner join pg_class ic
                              on ic.oid = i.indexrelid
                      where i.indrelid = t.oid and
                            ic.relname not like '%\_tat') i
  left join lateral (select uni.contype,
                            array_agg(a.attname order by a.attnum) filter (where a.attnotnull) as pk_columns,
                            array_agg(a.atttypid::regtype::text order by a.attnum) filter (where a.attnotnull) as pk_types,
                            count(1)
                       from pg_constraint uni
                      inner join pg_attribute a
                              on a.attnum = any(uni.conkey)
                      where uni.conrelid = t.oid and
                            uni.contype in ('p', 'u') and
                            a.attrelid = t.oid
                      group by 1
                     having cardinality(array_agg(a.attname order by a.attnum) filter (where a.attnotnull)) = count(1) --only all not null columns
                      order by 3
                      limit 1) as pk
         on true
 cross join lateral (select coalesce(array_agg(format(
                                                 'alter table %s add constraint %s %s using index %s%s%s;',
                                                 tn.table_name,
                                                 uni.conname,
                                                 case
                                                   when uni.contype = 'p'
                                                     then 'primary key'
                                                   else 'unique'
                                                 end,
                                                 uni.conname,
                                                 case
                                                   when uni.condeferrable
                                                     then ' deferrable'
                                                 end,
                                                 case
                                                   when uni.condeferred
                                                     then ' initially deferred'
                                                 end)),
                                     '{}') as create_constraints
                       from pg_constraint uni
                      where uni.conrelid = t.oid and
                            uni.contype in ('p', 'u')) uni
 cross join lateral (select coalesce(array_agg(format('alter table %s__tat_new add constraint %s %s;',
                                                      tn.table_name,
                                                      chk.conname,
                                                      pg_get_constraintdef(chk.oid))),
                                     '{}') as create_constraints
                       from pg_constraint chk
                      where chk.conrelid = t.oid and
                            chk.contype = 'c' and
                            chk.conname not like '%\_tat') chk
 cross join lateral (select coalesce(array_agg(format('alter table %s add constraint %s %s not valid;',
                                                      fk.conrelid::regclass::text,
                                                      fk.conname,
                                                      pg_get_constraintdef(fk.oid))),
                                     '{}') as create_constraints,
                            coalesce(array_agg(format('alter table %s validate constraint %s;',
                                                      fk.conrelid::regclass::text,
                                                      fk.conname)),
                                     '{}') as validate_constraints,
                            coalesce(array_agg(format('alter table %s drop constraint %s;',
                                                      fk.conrelid::regclass::text,
                                                      fk.conname))
                                              filter (where fk.conrelid <> t.oid),
                                     '{}') as drop_constraints
                       from pg_constraint fk
                      where (fk.conrelid = t.oid
                             or
                             fk.confrelid = t.oid) and
                            fk.contype = 'f') fk
 cross join lateral (select coalesce(array_agg(format('grant %s on table %s__tat_new to "%s";',
                                                      p.privileges,
                                                      tn.table_name,
                                                      p.grantee)),
                                     '{}') as grant_privileges
                       from (select g.grantee, string_agg(g.privilege_type, ', ') as privileges
                               from information_schema.role_table_grants g
                              where g.table_name = t.relname and
                                    g.table_schema = t.relnamespace::regnamespace::text and
                                    g.grantee <> 'postgres'
                              group by g.grantee) p) p
 cross join lateral (select coalesce(array_agg(pg_get_triggerdef(tg.oid) || ';'), '{}') as create_triggers
                       from pg_trigger tg
                      where tg.tgrelid = t.oid and
                            not tgisinternal and
                            tg.tgname not like '%__tat_delta') tg
 cross join lateral (select json_object_agg(
                              a.attname, json_build_object(
                                           'type', ft.type,
                                           'not_null', case
                                                         when a.attnotnull
                                                           then ' not null'
                                                         else ''
                                                       end,
                                           'default', coalesce(' default ' || pg_get_expr(cd.adbin, cd.adrelid), ''),
                                           'collate', coalesce(' collate ' || quote_ident(coll.collname), ''),
                                           'comment', case
                                                        when cc.description is not null
                                                          then format('comment on column %s__tat_new.%I is %L;',
                                                                      a.attrelid::regclass, a.attname, cc.description)
                                                      end)
                              order by a.attnum) as all_columns,
                            coalesce(array_agg(format('alter sequence %s owned by %s__tat_new.%s;',
                                                      s.serial_sequence,
                                                      tn.table_name,
                                                      a.attname))
                                              filter (where s.serial_sequence is not null),
                                     '{}') as alter_sequences
                       from pg_attribute a
                      cross join format_type(a.atttypid, a.atttypmod) as ft(type)
                      inner join pg_type ct
                              on ct.oid = a.atttypid
                       left join pg_collation coll
                              on coll.oid = a.attcollation and
                                 a.attcollation <> ct.typcollation
                       left join pg_attrdef cd
                              on cd.adrelid = a.attrelid and
                                 cd.adnum = a.attnum
                       left join pg_description cc
                              on cc.objoid = a.attrelid and
                                 cc.classoid = 'pg_class'::regclass and
                                 cc.objsubid = a.attnum
                      cross join pg_get_serial_sequence(tn.table_name, a.attname) as s(serial_sequence)
                      where a.attrelid = t.oid and
                            a.attnum > 0 and
                            not a.attisdropped) att
 cross join lateral (select coalesce(array_agg(format('create view %s as %s; %s;',
                                                      v.oid::regclass::text,
                                                      replace(replace(replace(pg_get_viewdef(v.oid),
                                                                              format('timezone(''Europe/Moscow''::text, %s.start_time) AS start_time', t.relname),
                                                                              format('%s.start_time', t.relname)),
                                                                      format('timezone(''Europe/Moscow''::text, %s.date_time) AS date_time', t.relname),
                                                                      format('%s.date_time', t.relname)),
                                                              format('timezone(''Europe/Moscow''::text, %s.hit_time) AS hit_time', t.relname),
                                                              format('%s.hit_time', t.relname)),
                                                      (select string_agg(format('%s; %s;', pg_get_functiondef(pgt.tgfoid), pg_get_triggerdef(pgt.oid)), E';\n')
                                                         from pg_trigger pgt
                                                        where pgt.tgrelid = v.oid::regclass))
                                               order by v.oid),
                                     '{}') as create_views,
                            coalesce(json_agg(json_build_object('obj_name', v.oid::regclass,
                                                                'obj_type', 'table',
                                                                'acl', v.relacl))
                                             filter (where v.relacl is not null),
                                     '[]') as view_acl_to_grants_params,
                            coalesce(array_agg(format('comment on view %s is %L;',
                                                      v.oid::regclass, d.description))
                                              filter (where d.description is not null),
                                     '{}') as comment_views,
                            coalesce(array_agg(format('drop view %s;',
                                                      v.oid::regclass)
                                               order by v.oid desc),
                                     '{}') as drop_views,
                            array_agg(v.reltype) as view_type_oids
                       from pg_class v
                       left join pg_description d
                              on d.objoid = v.oid
                      where v.relkind = 'v' and
                            v.oid in (with recursive w_depend as (
                                        select rw.ev_class
                                          from pg_depend d
                                         inner join pg_rewrite rw
                                                 on rw.oid = d.objid
                                         where d.refobjid = t.oid
                                        union
                                        select rw.ev_class
                                          from w_depend w
                                         inner join pg_depend d
                                                 on d.refobjid = w.ev_class
                                         inner join pg_rewrite rw
                                                 on rw.oid = d.objid
                                      )
                                      select d.ev_class
                                        from w_depend d)) v
 cross join lateral (select coalesce(array_agg(pg_catalog.pg_get_functiondef(f.oid) || ';'), '{}') as create_functions,
                            coalesce(json_agg(json_build_object(
                                                'obj_name', format('%s(%s)', f.oid::regproc, pg_get_function_identity_arguments(f.oid)),
                                                'obj_type', case
                                                              when f.prokind = 'p'
                                                                then 'procedure'
                                                              else 'function'
                                                            end,
                                                'acl', f.proacl))
                                             filter (where f.proacl is not null),
                                     '[]') as function_acl_to_grants_params,
                            coalesce(array_agg(format('drop function %s(%s);',
                                                      f.oid::regproc::text,
                                                      pg_get_function_identity_arguments(f.oid))),
                                     '{}') as drop_functions
                       from pg_proc f
                      where f.prorettype = t.reltype
                            or
                            t.reltype = any(f.proargtypes)
                            or
                            t.reltype = any(f.proallargtypes)
                            or
                            f.prorettype = any(v.view_type_oids)) f
 cross join lateral (select coalesce(array_agg(format('alter table %s set (%s);', t.oid::regclass, ro.option)), '{}') as storage_parameters
                       from unnest(t.reloptions) as ro(option)) sp
 cross join lateral (select array_agg(i.inhparent::regclass::text) as inherits
                       from pg_inherits i
                      where i.inhrelid = t.oid) as inh
  cross join lateral (select case
                              when t.relpartbound is not null
                                then pg_get_expr(t.relpartbound, t.oid)
                            end as attach_expr) as attach
  left join lateral (select format(
                              ' partition by %s (%s)',
                              case p.partstrat
                                when 'r' then 'range'
                                when 'l' then 'list'
                                when 'h' then 'hash'
                              end,
                              (select string_agg(a.attname, ', ') --FIXME: need add expration
                                 from unnest(p.partattrs::int[]) i
                                 left join pg_attribute a
                                        on a.attrelid = t.oid and
                                           a.attnum = i)) as partition_expr
                       from pg_partitioned_table p
                      where p.partrelid = t.oid) part
         on true
  left join format('alter table %s replica identity %s;',
                    t.oid::regclass,
                    case t.relreplident
                      when 'f'
                        then 'full'
                      when 'n'
                        then 'nothing'
                      when 'i'
                        then format('using index %I',
                                    (select cr.relname
                                       from pg_index ir
                                      inner join pg_class cr
                                              on cr.oid = ir.indexrelid
                                      where ir.indrelid = t.oid and
                                            ir.indisreplident))
                    end) as ri(replica_identity)
         on t.relreplident in ('f', 'n', 'i')
 cross join lateral (select coalesce(
                              array_agg(
                                format('alter publication %I add table %s;',
                                       p.pubname,
                                       t.oid::regclass)),
                              '{}') as publications
                       from pg_publication_rel pr
                      inner join pg_publication p
                              on p.oid = pr.prpubid
                      where pr.prrelid = t.oid) pb
 where t.oid = any($1::regclass[])
