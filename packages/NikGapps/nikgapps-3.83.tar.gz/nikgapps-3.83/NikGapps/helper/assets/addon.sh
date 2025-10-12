#!/sbin/sh

destDir=$system/addon.d
NikGappsDir=$destDir
addon_index=10
fileName=$1
installSource=$2
deleteSource=$2
debloaterSource=$2
[ -n "$3" ] && addon_index=$3
mkdir -p "$destDir"
TMPDIR=/dev/tmp
COMMONDIR=$TMPDIR/NikGappsScripts
if $BOOTMODE; then
  COMMONDIR=$MODPATH/NikGappsScripts
  mkdir -p "$COMMONDIR"
fi
addonDir="/sdcard/NikGapps/addonLogs"
nikGappsTestLog="$addonDir/logfiles/NikGapps.log"
newline='
'

echo_add_to_log() {
  echo ""
  echo "addToLog() {"
  echo "  echo \"\$(date +%Y_%m_%d_%H_%M_%S): \$1\" >> \$nikGappsAddonLogFile"
  echo "}"
  echo ""
}

echo_add_file_to_log() {
  echo ""
  echo "addFileToLog() {"
  echo "  output_path=\$(get_output_path \"\$1\")"
  echo "  if [ -f \"\$output_path\" ]; then"
  echo "    size=\$(du -h \"\$output_path\" | awk '{print \$1}')"
  echo "    echo \"\$(date +%Y_%m_%d_%H_%M_%S): - \$output_path copied, Size: \$size\" >> \$nikGappsAddonLogFile"
  echo "  else"
  echo "    echo \"\$(date +%Y_%m_%d_%H_%M_%S): - \$output_path does not exist\" >> \$nikGappsAddonLogFile"
  echo "  fi"
  echo "}"
  echo ""
}

get_addond_filename() {
    prop_file="$1"
    prefix="$2"
    if [ ! -f "$prop_file" ]; then
        addToLog "- Prop file not found. Creating one with a fresh 'addond' entry." "$fileName"
        echo "$prefix-01-$fileName.sh"
        return
    fi
    addond_entry=$(grep "^addond=$prefix-[0-9]*-.*\.sh$" "$prop_file" | head -n 1 | cut -d'=' -f2)
    num_entries=$(grep -c "^addond=$prefix-[0-9]*-.*\.sh$" "$prop_file")
    addToLog "- $num_entries entries with $prefix prefix found" "$fileName"
    [ -n "$addond_entry" ] && addToLog "- $addond_entry" "$fileName"
    if [ "$num_entries" -gt 1 ]; then
        addToLog "- Found multiple 'addond' entries. Deleting the rest." "$fileName"
        sed -i '/^addond=/ {n; d}' "$prop_file"
    fi
    echo "$addond_entry"
}

generate_filename() {
  directory="$1"; prefix="$2"; app_name="$3"
  max_index=0
  for file in "$directory"/"$prefix"-[0-9]*-"$app_name".sh; do
    [ -e "$file" ] || continue
    index=$(basename "$file" | cut -d '-' -f 2 | sed 's/[^0-9]*//g')
    if [ "$index" -eq "$index" ] 2>/dev/null; then
      echo "$file"
      return
    fi
  done
  for file in "$directory"/*.sh; do
    if grep -q "AFZC" "$file"; then
      file_name=$(basename "$file")
      file_constant=$(echo "$file_name" | cut -d '-' -f 1)
      if [ "$file_constant" = "$prefix" ]; then
        index=$(echo "$file_name" | cut -d '-' -f 2 | sed 's/[^0-9]*//g')
        if [ -n "$index" ] && [ "$index" -eq "$index" ] 2>/dev/null; then
          [ "$index" -gt "$max_index" ] && max_index="$index"
        fi
      fi
    fi
  done
  max_index="${max_index#0}"
  max_index=$((max_index + 1))
  new_file="$directory/$prefix-$(printf "%02d" "$max_index")-$app_name.sh"
  echo "$new_file"
}

update_addond_filename() {
    prop_file="$1"
    new_filename="$2"
    if [ ! -f "$prop_file" ]; then
        addToLog "- Prop file not found. Creating one with a fresh 'addond' entry." "$fileName"
        addToLog "- addond=$new_filename >> $prop_file" "$fileName"
        echo "addond=$new_filename" > "$prop_file"
        return
    fi
    if ! grep -q '^addond=' "$prop_file"; then
        addToLog "- Entry not found. Creating one with a fresh 'addond' entry." "$fileName"
        addToLog "- addond=$new_filename >> $prop_file" "$fileName"
        echo "addond=$new_filename" >> "$prop_file"
    else
        addToLog "- Entry found. Updating the entry." "$fileName"
        addToLog "- addond=$new_filename >> $prop_file" "$fileName"
        sed -i "s/^\(addond=\).*/\1$new_filename/" "$prop_file"
        num_entries=$(grep -c '^addond=' "$prop_file")
        if [ "$num_entries" -gt 1 ]; then
            addToLog "- Found multiple 'addond' entries. Deleting the rest." "$fileName"
            sed -i '/^addond=/ {n; d}' "$prop_file"
        fi
    fi
}


list_build_props() {
  echo ""
  echo "list_build_props() {"
  echo "cat <<EOF"

  if [ -f "$installSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "buildprop=" "$installSource" | cut -d= -f2-)
    for i in $g; do
      echo "$i"
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

list_files() {
  echo ""
  echo "list_files() {"
  echo "cat <<EOF"

  if [ -f "$installSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "install=" "$installSource" | cut -d= -f2)
    for i in $g; do
      if [ -f "$system/$i" ]; then
        echo "$i"
      fi
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

list_delete_folders() {
  echo ""
  echo "delete_folders() {"
  echo "cat <<EOF"

  if [ -f "$deleteSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "delete=" "$deleteSource" | cut -d= -f2)
    for i in $g; do
      echo "$i"
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

list_force_delete_folders() {
  echo ""
  echo "force_delete_folders() {"
  echo "cat <<EOF"

  if [ -f "$deleteSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "forceDelete=" "$deleteSource" | cut -d= -f2)
    for i in $g; do
      echo "$i"
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

list_debloat_folders() {
  echo ""
  echo "debloat_folders() {"
  echo "cat <<EOF"

  if [ -f "$debloaterSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "debloat=" "$debloaterSource" | cut -d= -f2)
    for i in $g; do
      echo "$i"
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

list_force_debloat_folders() {
  echo ""
  echo "force_debloat_folders() {"
  echo "cat <<EOF"

  if [ -f "$debloaterSource" ]; then
    OLD_IFS="$IFS"
    IFS="$(printf '%b_' ' \n')"
    IFS="${IFS%_}"
    g=$(grep "forceDebloat=" "$debloaterSource" | cut -d= -f2)
    for i in $g; do
      echo "$i"
    done
    IFS="$OLD_IFS"
  fi

  echo "EOF"
  echo "}"
  echo ""
}

pre_backup() {
  echo " pre-backup)"
  echo "   if [ \"\$execute_config\" = \"0\" ]; then"
  echo "     deleted=false"
  echo "     for dir in \"\$S/addon.d/\" \"\$T/addon.d/\"; do"
  echo "       for file in \"\$dir\"*\"$fileName.sh\"; do"
  echo "         if [ -f \"\$file\" ]; then"
  echo "           if [ \"\$deleted\" = false ]; then"
  echo "             ui_print \"- Deleting \$(basename \$file)\""
  echo "             deleted=true"
  echo "           fi"
  echo "           rm -f \"\$file\""
  echo "         else"
  echo "           addToLog \"- \$file does not exist.\""
  echo "         fi"
  echo "       done"
  echo "     done"
  echo "     exit 1"
  echo "   fi"
  echo " ;;"
}

backup() {
  echo " backup)"
  echo "   if [ \"\$execute_config\" = \"1\" ]; then"
  echo "     ui_print \"- Backing up $fileName\""
  echo "     list_files | while read FILE DUMMY; do"
  echo "       backup_file \$S/\"\$FILE\""
  echo "     done"
  echo "   fi"
  echo " ;;"
}

restore() {
  echo " restore)"
  echo "   if [ \"\$execute_config\" = \"1\" ]; then"
  echo "     addToLog \" \""
  echo "     ui_print \"- Restoring $fileName\""
  echo "     delete_in_system \"\$(delete_folders)\" \"Deleting aosp app\""
  echo "     delete_in_system \"\$(force_delete_folders)\" \"Force Deleting\""
  echo "     delete_in_system \"\$(debloat_folders)\" \"Debloating\""
  echo "     delete_in_system \"\$(force_debloat_folders)\" \"Force Debloating\""
  echo "     list_files | while read FILE REPLACEMENT; do"
  echo "       R=\"\""
  echo "       [ -n \"\$REPLACEMENT\" ] && R=\"\$S/\$REPLACEMENT\""
  echo "       [ -f \"\$C/\$S/\$FILE\" ] && restore_file \$S/\"\$FILE\" \"\$R\" && addFileToLog \"\$S/\$FILE\""
  echo "     done"
  echo "     for i in \$(list_files); do"
  echo "       f=\$(get_output_path \"\$S/\$i\")"
  echo "       chown root:root \"\$f\""
  echo "       chmod 644 \"\$f\""
  echo "       chmod 755 \$(dirname \$f)"
  echo "     done"
  echo "     if list_build_props | grep -q '.'; then"
  echo "       restore_build_props"
  echo "     fi"
  echo "   fi"
  echo " ;;"
}

run() {
  echo " "
  echo "case \"\$1\" in"
  pre_backup
  backup
  restore
  echo "esac"
}

# Read the config file from (Thanks to xXx @xda)
ReadConfigValue() {
  value=$(sed -e '/^[[:blank:]]*#/d;s/[\t\n\r ]//g;/^$/d' "$2" | grep "^$1=" | cut -d'=' -f 2)
  echo "$value"
  return $?
}

header() {
  echo "#!/sbin/sh"
  echo "#"
  echo "# ADDOND_VERSION=3"
}

# this approach is for a rainy day, now it works fine without it.
#dest="$destDir/$(get_addond_filename "$installSource" "$addon_index")"
#[ "$dest" = "$destDir/" ] && dest="$(generate_filename "$destDir" "$addon_index" "$fileName")"

dest="$(generate_filename "$destDir" "$addon_index" "$fileName")"
addToLog "- dest=$dest" "$fileName"

for i in $(find $destDir -iname "*$fileName.sh" 2>/dev/null;); do
  if [ -f "$i" ]; then
    rm -rf "$i"
  fi
done

header > "$dest"
cat "$COMMONDIR/header.sh" >> "$dest"
{
  echo_add_to_log
  echo_add_file_to_log
  cat "$COMMONDIR/functions.sh"
  list_build_props
  list_files
  list_delete_folders
  list_force_delete_folders
  list_debloat_folders
  list_force_debloat_folders
  run
} >>"$dest"
chmod 755 "$dest"
# rainy day stuff
# update_addond_filename "$installSource" "$(basename "$dest")"
mkdir -p "$addon_scripts_logDir"
cat "$dest" > "$addon_scripts_logDir/$(basename "$dest")"